import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from PIL import Image, ImageTk

from datetime import datetime
from report_generator import ReportGenerator
import os

import logging
logger = logging.getLogger(__name__)

class ReportGeneratorApp:
    def __init__(self, root):
        if not os.path.exists('./logs'):
            os.mkdir('./logs')
        logging.basicConfig(filename='./logs/main.log', level=logging.INFO, format='%(asctime)s %(message)s', encoding='utf8')
        self.root = root
        self.root.title("Gerador de Relatórios - Sistema Empresarial")
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        # Configuração de estilo
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()

        # Frame principal
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Cabeçalho
        self.create_header()

        # Generate Button
        self.processing = False
        self.loading_frames = []

        # Formulário
        self.create_form()

        # Área de status/resultado
        self.create_status_area()

        # Rodapé
        self.create_footer()
        self.reports_running = []
        self.cur_row = 0


    def configure_styles(self):
        """Configura os estilos visuais dos componentes"""
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Helvetica', 10))
        self.style.configure('Header.TLabel',
                             font=('Helvetica', 16, 'bold'),
                             foreground='#2c3e50')
        self.style.configure('TButton',
                             font=('Helvetica', 10),
                             padding=6)
        self.style.configure('Generate.TButton',
                             foreground='white',
                             background='#27ae60',
                             font=('Helvetica', 10, 'bold'))
        self.style.configure('StatusRow.TFrame',
                             background='#f0f0f0',
                             relief=tk.SUNKEN)
        self.style.configure('StatusRow.TLabel', font=('Helvetica', 9))
        self.style.map('Generate.TButton',
                       background=[('active', '#2ecc71'), ('pressed', '#219653')])
        self.style.configure('TCombobox', padding=5)
        self.style.configure('Status.TFrame', background='white', relief=tk.SUNKEN)
        self.style.configure('Status.TLabel', background='white', font=('Helvetica', 9))

    def create_header(self):
        """Cria o cabeçalho da aplicação"""
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))

        logo_label = ttk.Label(header_frame,
                               text="RELATÓRIOS EMPRESARIAIS",
                               style='Header.TLabel')
        logo_label.pack(side=tk.LEFT)

        # Adicionar espaço para um logo real se necessário
        # logo_image = tk.PhotoImage(file="logo.png")
        # logo = ttk.Label(header_frame, image=logo_image)
        # logo.pack(side=tk.RIGHT)

    def create_form(self):
        """Cria o formulário de entrada de dados"""
        form_frame = ttk.LabelFrame(self.main_frame,
                                    text="Parâmetros do Relatório",
                                    padding=(20, 10))
        form_frame.pack(fill=tk.X, pady=(0, 20))

        # Mês de competência
        ttk.Label(form_frame, text="Mês de Competência:").grid(
            row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.month_entry = DateEntry(
            form_frame,
            locale='pt_BR',
            date_pattern='dd/mm/yyyy',
            year=datetime.now().year,
            month=datetime.now().month,
            day=1,
            mindate=datetime(2000, 1, 1),
            maxdate=datetime(2100, 12, 31),
            showweeknumbers=False,
            showothermonthdays=False)
        self.month_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        # Seleção de empresa
        ttk.Label(form_frame, text="Empresa:").grid(
            row=1, column=0, padx=5, pady=5, sticky=tk.W)

        # Lista de empresas (pode ser carregada de um banco de dados)
        companies = [
            "NutriArt",
            "TCM",
        ]

        self.company_combo = ttk.Combobox(
            form_frame,
            values=companies,
            state="readonly")
        self.company_combo.current(0)
        self.company_combo.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        self.image_check = Image.open('assets/green_check.jpg')
        self.image_check = ImageTk.PhotoImage(self.image_check.resize((20, 20), Image.LANCZOS).copy())

        self.image_error = Image.open('assets/error.webp')
        self.image_error = ImageTk.PhotoImage(self.image_error.resize((20, 20), Image.LANCZOS).copy())
        gif = Image.open('assets/loading.gif')

        for frame in range(0, gif.n_frames):
            gif.seek(frame)
            frame_image = ImageTk.PhotoImage(gif.resize((20, 20), Image.LANCZOS).copy())
            self.loading_frames.append(frame_image)
        self.frame_count = len(self.loading_frames)
        self.current_frame = 0

        # loading_img = loading_img.subsample(10, 10)
        # Botão de gerar relatório
        self.generate_btn = ttk.Button(form_frame, text="Gerar Relatório", style='Generate.TButton', command=self.generate_report)
        self.generate_btn.grid(row=2, column=0, columnspan=2, pady=15)

    def animate_loading(self, label):
        self.current_frame = (self.current_frame + 1) % self.frame_count
        label.config(image=self.loading_frames[self.current_frame]) # Ajuste o delay conforme o GIF

    def create_status_area(self):
        """Cria a área de status/resultado"""
        self.status_frame = ttk.Frame(self.main_frame, style='Status.TFrame', padding=10)
        self.status_frame.pack(fill=tk.BOTH, expand=True)


        self.status_label = ttk.Label(
            self.status_frame,
            text="Preencha os parâmetros e clique em 'Gerar Relatório'",
            style='Status.TLabel')

        # self.status_label.pack(anchor=tk.W)

    def add_status_observer(self, company, competence, thread):
        status_frame_row = ttk.Frame(self.status_frame, style='StatusRow.TFrame')
        status_frame_row.pack(fill=tk.X, pady=4)

        status_label = ttk.Label(status_frame_row, image=self.loading_frames[0], style='StatusRow.TLabel')
        status_label.grid(row=self.cur_row, column=0, padx=5, pady=5, sticky=tk.W)

        message_label = ttk.Label(status_frame_row, text=f"Gerando relatório para {company} - {competence} (Carregando NFes)", style='StatusRow.TLabel')
        message_label.grid(row=self.cur_row, column=1, padx=5, pady=5, sticky=tk.W)

        progress_bar = ttk.Progressbar(status_frame_row, orient="horizontal", length=200, mode="determinate",
                    takefocus=True)
        progress_bar.grid(row=self.cur_row, column=2, padx=5, pady=5, sticky=tk.W)

        # cancel_button = ttk.Button(status_frame_row, text='X', width=10, command=lambda : self.cancel_thread(thread, status_label, progress_bar))
        # cancel_button.grid(row=self.cur_row, column=3, padx=5, pady=5, sticky=tk.W)


        self.cur_row += 1
        self.verify_thread(thread, status_label, message_label, progress_bar, company, competence)

    def cancel_thread(self, thread, status_label, progress_bar):
        thread.stop()
        status_label.config(image=self.image_error)
        progress_bar['value'] = 0

    def create_footer(self):
        """Cria o rodapé da aplicação"""
        footer_frame = ttk.Frame(self.main_frame)
        footer_frame.pack(fill=tk.X, pady=(20, 0))

        ttk.Label(
            footer_frame,
            text="© 2025 Sistema de Relatórios Empresariais - Versão 1.0",
            font=('Helvetica', 8)).pack(side=tk.RIGHT)

    def generate_report(self):
        """Função para gerar o relatório com base nos parâmetros selecionados"""
        self.processing = True

        month_year = self.month_entry.get_date()
        company = self.company_combo.get()
        if not month_year or not company:
            messagebox.showerror("Erro", "Preencha todos os campos!")
            return
        # try:
        if company == 'TCM':
            sold_code = 934031
        elif company == 'NutriArt':
            sold_code = 3494091
        else:
            raise

        # Formata a data
        competence = month_year.strftime("%m/%Y")
        logger.info(f'Iniciando Geração de relatório para a empresa {company} para competência {competence}')
        for report_running in self.reports_running:
            if report_running['company'] == company and report_running['competence'] == competence:
                logger.warning(f'Já está sendo executada a geração do relatório da empresa {company} para a competência {competence}!')
                messagebox.showinfo("Aviso", f"Já está sendo executada a geração do relatório da empresa {company} para a competência {competence}!")
                return
        self.reports_running.append({'company': company, 'competence': competence})

        # self.status_label.config(text=f'Gerando relatório para {company} - {competence}')

        report_generator_thread = ReportGenerator(company, sold_code, month_year.month, month_year.year, True)
        report_generator_thread.start()

        self.add_status_observer(company, competence, report_generator_thread)

        # except Exception as e:
        #     messagebox.showerror("Erro", f"Ocorreu um erro ao gerar o relatório:\n{str(e)}")

    def verify_thread(self, thread, label, message_label, progress_bar, company, competence):
        if thread.is_alive():
            if thread.exception:
                print(f'Exception na thread: {thread.exception}')
            self.animate_loading(label)
            root.after(100, lambda: self.verify_thread(thread, label, message_label, progress_bar, company, competence))
            progress_bar.configure(maximum=thread.nfe_total)
            progress_bar['value'] = thread.nfe_count
            if 0 < thread.nfe_total == thread.nfe_count:
                message_label.configure(text=f"Gerando relatório para {company} - {competence} (Carregando pedidos)")
                progress_bar.configure(maximum=thread.registers_total)
                progress_bar['value'] = thread.registers_cur


        else:
            label.config(image=self.image_check)



if __name__ == "__main__":
    root = tk.Tk()
    app = ReportGeneratorApp(root)
    root.mainloop()