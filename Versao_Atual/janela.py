''' A parte Gráfica será dividida em 3 Frames, lado a lado
    e 2 Menus:

    FRAMES 
    - Primeiro Frame:
        Será composto pelo Output da Aplicação, onde ficarão
        o gráfico de nível de energia e os eventuais textos de
        controle da Serial
    
    - Segundo Frame:
        Será composto por duas partes, uma em cima da outra:
            . A parte de cima deste Frame ficará com a Caixa de Música, 
            onde serão exibidas as músicas disponíveis; com o controle
            deslizante da posição (Slider) que indica o instante atual 
            da música, sendo possível arrastá-lo para a posição desejada;
            e o tempo decorrido da música, ou seja, o instante em que 
            ela se encontra.
            . A parte de baixo será composta pelos 5 botões (anterior,
            stop, play, pause e próxima) e por um texto informando o
            nome da música tocando atualmente.
            
    - Terceiro Frame:
        Será composto pelo controle deslizante (Slider) do volume, sendo
        possível arrastá-lo para o volume desejado.
        

    MENUS
    - Primeiro Menu:
        Será composto por duas opções: adicionar UMA Música e adicionar
    VÁRIAS músicas. Usuário poderá escolher um ou vários arquivos 
    para serem tocados.

    - Segundo Menu:
        Será composto por duas opções: apagar UMA música (aquela que se
        encontra selecionada) ou apagar TODAS as músicas.'''


from tkinter import *
from PIL import Image, ImageTk
import pygame
from tkinter import filedialog
import time
import librosa
import tkinter.ttk as ttk
import tkinter as tk
from tkinter import messagebox
import tkinter.filedialog as filedialog
from PIL import ImageTk, Image
import subprocess
import os
import numpy as np

caminho_imagens = "Imagens/"

global pausada 
pausada = False

global duracao_musica_tocando, nome_musica_tocando, arquivo_musica_tocando
duracao_musica_tocando = 0
nome_musica_tocando = ""
arquivo_musica_tocando = ""

global taxa_amostragem, media_energia_musica
taxa_amostragem = 0
media_energia_musica = np.zeros(1)

global y, sr
y = 0
sr = 0

global parou
parou = False

# os timers recorrentes das músicas ficarão nesta variável
global musicas_after_id
musicas_after_id = None

# os timers recorrentes dos níveis de energia dos intrumentos ficarão nesta variável
global energias_after_id
energias_after_id = None

# dicionario_musicas: {"caminho": str, "nome": str, "tipo": str}
dicionario_musicas = {}

root = Tk()
root.title('Micro B5')
root.geometry("900x400")

'''Inicializando Pygame Mixer'''
pygame.mixer.init()
taxa_amostragem = pygame.mixer.get_init()[0]


''' Funções do Menu de Adição de Músicas '''
# adiciona UMA música a Playlist
def adiciona_musica():
    string_arquivo = filedialog.askopenfilename(title="Escolha uma música", filetypes=(("mp3 Files", "*.mp3"), ("wav Files", "*.wav"), ("ogg Files", "*.ogg"), ))
    
    string_caminho = ""
    string_nome = ""
    string_tipo = ""

    string_caminho = string_arquivo[0:string_arquivo.rfind('/')+1]
    # renomeando a variável música para não aparecer ao usuário o caminho de onde está a música e o .tipo da música
    string_nome = string_arquivo.replace(string_caminho, "")
    
    if ".mp3" in string_nome:
        string_nome = string_nome.replace(".mp3", "")
        string_tipo = "mp3"
    elif ".wav" in string_nome:
        string_nome = string_nome.replace(".wav", "")
        string_tipo = "wav"
    elif ".ogg" in string_nome:
        string_nome = string_nome.replace(".ogg", "")
        string_tipo = "ogg"

    nova_musica = [string_caminho, string_nome, string_tipo]
    dicionario_musicas[len(dicionario_musicas)] = nova_musica
    
    # adiciona música ao final da lista da caixa de música
    caixa_musica.insert(END, string_nome)


# adiciona VÁRIAS músicas à Playlist
def adiciona_varias_musicas():
    string_musicas = filedialog.askopenfilenames(title="Escolha uma música", filetypes=(("mp3 Files", "*.mp3"), ("wav Files", "*.wav"), ("ogg Files", "*.ogg"), ))
    
    # adiciona músicas à Caixa de Música
    for musica in string_musicas:
        string_caminho = ""
        string_nome = ""
        string_tipo = ""

        string_caminho = musica[0:musica.rfind('/')+1]
        # renomeando a variável música para não aparecer ao usuário o caminho de onde está a música e o .tipo da música
        string_nome = musica.replace(string_caminho, "")
        
        if ".mp3" in string_nome:
            string_nome = string_nome.replace(".mp3", "")
            string_tipo = "mp3"
        elif ".wav" in string_nome:
            string_nome = string_nome.replace(".wav", "")
            string_tipo = "wav"
        elif ".ogg" in string_nome:
            string_nome = string_nome.replace(".ogg", "")
            string_tipo = "ogg"

        nova_musica = [string_caminho, string_nome, string_tipo]
        dicionario_musicas[len(dicionario_musicas)] = nova_musica
        
        # adiciona música ao final da lista da caixa de música
        caixa_musica.insert(END, string_nome)


''' Funções do Menu de Deleção de Músicas '''
# deleta UMA música da Playlist
def deletar_musica():
    parar()
    pygame.mixer.music.stop()
    nome_arq = caixa_musica.get(ACTIVE)
    caixa_musica.delete(ACTIVE)
    chave = retorna_posicao_dicionario(nome_arq)
    dicionario_musicas.pop(chave)
    reseta_textos()

# deletar TODAS as músicas da Playlist
def deletar_todas_musicas():
    parar()
    pygame.mixer.music.stop()
    caixa_musica.delete(0, END)
    dicionario_musicas.clear()
    reseta_textos()


''' Funções utilitárias/auxiliares '''
# Função que redimensiona imagens para um quadrado com o num de pixels passado como parâmetro 
def redimensiona_imagem(nome, num_pixels):
    imagem = Image.open(caminho_imagens+nome)
    imagem_edit = imagem.resize((num_pixels, num_pixels))
    imagem_nova = ImageTk.PhotoImage(imagem_edit)

    return imagem_nova

# Função que retorna a posição de um arquivo pelo nome
# passado no parâmetro
def retorna_posicao_dicionario(nome_arq):
    for chave in dicionario_musicas:
        if dicionario_musicas[chave][1] == nome_arq:
            return chave
        
    return -1

# Função que procura pelo arquivo pelo nome no dicionario de músicas 
# e retorna string com o arquivo (caminho + nome + tipo)
def lista_nome_e_retorna_arq(nome_arquivo):
    chave = retorna_posicao_dicionario(nome_arquivo)
    if chave == -1:
        print('Arquivo não encontrado no Dicionário')
        return "0"
    
    caminho = dicionario_musicas[chave][0]
    nome = dicionario_musicas[chave][1]
    tipo = dicionario_musicas[chave][2]
    return caminho+nome+"."+tipo

# Função que define um Timer recorrente de 0.1s e
# que atualiza a Barra de Status e o Slider com a posição atual da música
def atualiza_posicao_atual_musica():
    global duracao_musica_tocando, nome_musica_tocando, parou, musicas_after_id
    
    if nome_musica_tocando == "" or parou:
        reseta_textos()
        return

    posicao_atual = pygame.mixer.music.get_pos()/1000
    posicao_atual_formatado = time.strftime("%M:%S", time.gmtime(posicao_atual))

    duracao_musica_formatado = time.strftime("%M:%S", time.gmtime(duracao_musica_tocando))
    
    if int(slider_posicao.get()) == int(duracao_musica_tocando):
        barra_status.config(text=f'Tempo decorrido: {duracao_musica_formatado}  de  {duracao_musica_formatado} ')
    elif pausada:
        pass
    elif int(slider_posicao.get()) == int(posicao_atual):
        # Slider não foi arrastado/movido
        posicao_atual += 1
        slider_posicao.config(to=int(duracao_musica_tocando), value=int(posicao_atual))
        barra_status.config(text=f'Tempo decorrido: {posicao_atual_formatado}  de  {duracao_musica_formatado} ')
    else:
        # Slider foi arrastado/movido
        slider_posicao.config(to=int(duracao_musica_tocando), value=int(slider_posicao.get()))
        posicao_atual_formatado = time.strftime("%M:%S", time.gmtime(int(slider_posicao.get())))
        barra_status.config(text=f'Tempo decorrido: {posicao_atual_formatado}  de  {duracao_musica_formatado} ')
        
        proximo_segundo = int(slider_posicao.get()) + 1
        slider_posicao.config(value=proximo_segundo)

    calcula_e_desenha_nivel_energia()

    # timer recorrente do TkInter
    musicas_after_id = barra_status.after(1000, atualiza_posicao_atual_musica)

# Função que reseta a Barra de Status e o Slider
def reseta_textos():
    global nome_musica_tocando, arquivo_musica_tocando

    nome_musica_tocando = ""
    arquivo_musica_tocando = ""
    barra_status.config(text='')
    slider_posicao.config(value=0)
    texto_musica_tocando.config(text='')
    desenha_niveis_energia(0, 0, 0, 0)
    label_status_batida.config(text='')
    label_energia_numerico.config(text='')


 # carrega, obtem o tamanho e formata a música com Librosa
def altera_musica_tocando(arquivo):
    global duracao_musica_tocando, nome_musica_tocando, arquivo_musica_tocando, taxa_amostragem, y, sr, media_energia_musica

    duracao_musica_tocando = librosa.get_duration(filename=arquivo)
    texto_musica_tocando.config(text=f'Música tocando: {nome_musica_tocando}')
    arquivo_musica_tocando = librosa.load(arquivo)
    
    # Load the audio file with librosa
    y, sr = librosa.load(arquivo, sr=taxa_amostragem)
    calcula_energia_media_musica()

# Função que desenha as barras dos níveis de energia de cada integrante da banda.
# Recebe como parâmteros 4 números de 0 a 200 para representar a energia
def desenha_niveis_energia(vocalista, baterista, baixista, pianista):
    if vocalista < 0 or baterista < 0 or baixista < 0 or pianista < 0:
        print("Algum valor está fora do intervalo [0, 200]!")
        return
    
    if vocalista > 200: 
        vocalista = 200
    if baterista > 200:
        baterista = 200
    if pianista > 200:
        pianista = 200
    if baixista > 200:
        baixista = 200

    canvas_vocalista.config(width=vocalista)
    canvas_baterista.config(width=baterista)
    canvas_baixista.config(width=baixista)
    canvas_pianista.config(width=pianista)

def calcula_energia_media_musica():
    global media_energia_musica, y, sr

    window_size = sr  # 1 second window size
    num_windows = len(y) // window_size
    energy_values = []

    for i in range(num_windows):
        start = i * window_size
        end = (i + 1) * window_size
        y_window = y[start:end]
        energy = np.sum(y_window ** 2)
        energy_values.append(energy)

    # Calcula a média das energias da música
    media_energia_musica = np.mean(energy_values)

# Calcula nível de energia da música corrente
def calcula_e_desenha_nivel_energia():
    global taxa_amostragem, media_energia_musica, y, sr

    posicao_atual = pygame.mixer.music.get_pos()/1000
    if posicao_atual == len(y):
        return

    y_window = y[int(posicao_atual * sr):int((posicao_atual + 1) * sr)]

    energy = np.sum(y_window ** 2)

    if energy < 0.001:
         energy = 0
    
    barra_energia = int(100*energy/media_energia_musica)
    desenha_niveis_energia(barra_energia, 0, 0, 0)

    label_energia_numerico.config(text=f"{int(energy)}")


# Função que seta a Label de Status das Batidas para SIM
def exibe_status_batidas_sim():
    label_status_batida.config(text="SIM", fg='green')

# Função que seta a Label de Status das Batidas para NÃO
def exibe_status_batidas_nao():
    label_status_batida.config(text="NÃO", fg='red')


''' Funções para separação do arquivo '''

def separate_audio(arquivo):
    global nome_musica_tocando

    output_dir = "output"
    messagebox.showinfo("Mensagem","Fazendo a separação de faixas, por favor aguarde.")
    texto_musica_tocando.config(text=f"Separando a música {nome_musica_tocando} em 5 faixas...")
    cmd = f"spleeter separate -p spleeter:5stems -o {output_dir} {arquivo}"
    print(cmd)
    subprocess.run(cmd, shell=True)
    messagebox.showinfo("Mensagem", "Separação de faixas concluída!")
    tocar()

def separate_file():
    global nome_musica_tocando
    if not dicionario_musicas:
        print("Dicionário vazio...")
        return
    parar()

    nome_musica_tocando = caixa_musica.get(ACTIVE)
    arquivo = lista_nome_e_retorna_arq(nome_musica_tocando)
    separate_audio(arquivo)



''' Função de Comando do Slider de Posição da Música '''
def deslizar_posicao(x):
    global nome_musica_tocando, arquivo_musica_tocando, taxa_amostragem
    arquivo_musica_tocando = lista_nome_e_retorna_arq(nome_musica_tocando)
    if arquivo_musica_tocando == "0":
        print("Música não encontrada")
    
    pygame.mixer.music.load(arquivo_musica_tocando)
    pygame.mixer.music.play(loops=0, start=int(slider_posicao.get()))
    if pausada:
        pygame.mixer.music.pause()


''' Função de Comando do Slider de Volume da Música '''
def deslizar_volume(x):
    pygame.mixer.music.set_volume(slider_volume.get())


''' Funções de Comando dos Botões '''
# toca música selecionada na Caixa de Música
def tocar():
    global parou, pausada, nome_musica_tocando, musicas_after_id, taxa_amostragem

    parou = False
    pausada = False

    if not dicionario_musicas:
        print("Dicionário vazio...")
        return

    nova_musica_selecionada = caixa_musica.get(ACTIVE)
    if nome_musica_tocando != "":
        barra_status.after_cancel(musicas_after_id)
        musicas_after_id = None
        reseta_textos()
        nome_musica_tocando = nova_musica_selecionada
    else:
        nome_musica_tocando = caixa_musica.get(ACTIVE)

    arquivo_musica = lista_nome_e_retorna_arq(nome_musica_tocando)
    if arquivo_musica == "0":
        print("Música não encontrada")

    altera_musica_tocando(arquivo_musica)
    atualiza_posicao_atual_musica()
    
    pygame.mixer.music.load(arquivo_musica)
    pygame.mixer.music.play(loops=0)

parou = False
# parar de tocar a música atual
def parar():
    global parou
    parou = True
    if not dicionario_musicas:
        print("Dicionário vazio...")
        return
    
    reseta_textos()

    pygame.mixer.music.stop()
    # tira o selecionado da música que estava selecionada
    caixa_musica.selection_clear(ACTIVE)

    # limpa a Barra de Status
    barra_status.config(text="")


# pausa/toca a música atual
def pausar():
    global parou, pausada

    if parou:
        parou = False

    if not dicionario_musicas:
        print("Dicionário vazio...")
        return
   
    # pausa a música
    if not pausada:
        pygame.mixer.music.pause()
        pausada = True
    else:
        # toca a música caso esteja pausada
        pygame.mixer.music.unpause()
        pausada = False

# toca a próxima música da Playlist da Caixa de Música
def proxima():
    global pausada, parou, nome_musica_tocando, taxa_amostragem
    if parou:
        parou = False
    if pausada:
        pausada = False

    reseta_textos()

    if not dicionario_musicas:
        print("Dicionário vazio...")
        return
    
    # pega, o formato tupla, a música que está tocando atualmente da playlist
    musica_atual = caixa_musica.curselection()
    if not musica_atual:
        return
    # adiciona 1 ao número da música atual
    proxima_musica = musica_atual[0] + 1
    if proxima_musica == caixa_musica.size():
        proxima_musica = 0
    
    # carrega e toca a próxima música
    nome_musica_tocando = caixa_musica.get(proxima_musica)

    arquivo_musica = lista_nome_e_retorna_arq(nome_musica_tocando)

    altera_musica_tocando(arquivo_musica)
    pygame.mixer.music.load(arquivo_musica)
    pygame.mixer.music.play(loops=0)

    # move a barra da música anterior para a atual
    caixa_musica.selection_clear(0, END)
    caixa_musica.activate(proxima_musica)
    caixa_musica.selection_set(proxima_musica, last=None)

# toca a música anterior à música corrente da Playlist
def anterior():
    global parou, pausada, nome_musica_tocando, taxa_amostragem
    if parou:
        parou = False
    if pausada:
        pausada = False

    reseta_textos()

    if not dicionario_musicas:
        print("Dicionário vazio...")
        return
    
    # pega, o formato tupla, a música que está tocando atualmente da playlist
    musica_atual = caixa_musica.curselection()
    if not musica_atual:
        return

    musica_anterior = 0
    # se a música atual for a primeira da Playlist, toca a última música
    if musica_atual[0] == 0:
        musica_anterior = caixa_musica.size()-1
    else:
        # subtrai 1 ao número da música atual
        musica_anterior = musica_atual[0] - 1
    
    # carrega e toca a música anterior
    nome_musica_tocando = caixa_musica.get(musica_anterior)
    arquivo_musica = lista_nome_e_retorna_arq(nome_musica_tocando)
    pygame.mixer.music.load(arquivo_musica)
    pygame.mixer.music.play(loops=0)

    altera_musica_tocando(arquivo_musica)

    # move a barra da música anterior para a atual
    caixa_musica.selection_clear(0, END)
    caixa_musica.activate(musica_anterior)
    caixa_musica.selection_set(musica_anterior, last=None)



''' Primeiro Frame '''
frame1 = Frame(root, bg="black", width=250)
frame1.pack(side=LEFT, fill=BOTH)
frame1.pack_propagate(0)

frame1_label_titulo = Label(frame1, text="OUTPUT", fg="white", bg="black", font=("Helvetica", 16))
frame1_label_titulo.pack(side=TOP, pady=5)

# Criar os Frames, as Labels e os Canvas de Níveis de Energia
frame1_nivel_energia = Frame(frame1, bg="black")
frame1_nivel_energia.pack(side=TOP, fill=BOTH, pady=5)

# Vocalista
frame1_nivel_energia_vocalista = Frame(frame1_nivel_energia, bg="white")
frame1_nivel_energia_vocalista.pack(side=TOP, fill=BOTH, padx=5, pady=8)
label = tk.Label(frame1_nivel_energia_vocalista, text="Vocalista", width=7, font='Helvetica 10 bold')
label.pack(side=LEFT)
canvas_vocalista = Canvas(frame1_nivel_energia_vocalista, height=30, bg="purple")
canvas_vocalista.pack(side=LEFT)

# Baterista
frame1_nivel_energia_baterista = Frame(frame1_nivel_energia, bg="white")
frame1_nivel_energia_baterista.pack(side=tk.TOP, fill=tk.BOTH, padx=5, pady=8)
label = tk.Label(frame1_nivel_energia_baterista, text="Baterista", width=7, font='Helvetica 10 bold')
label.pack(side=LEFT)
canvas_baterista = Canvas(frame1_nivel_energia_baterista, height=30, bg="green")
canvas_baterista.pack(side=LEFT)

# Baixista
frame1_nivel_energia_baixista = Frame(frame1_nivel_energia, bg="white")
frame1_nivel_energia_baixista.pack(side=TOP, fill=BOTH, padx=5, pady=8)
label = tk.Label(frame1_nivel_energia_baixista, text="Baixista", width=7, font='Helvetica 10 bold')
label.pack(side=LEFT)
canvas_baixista = tk.Canvas(frame1_nivel_energia_baixista, height=30, bg="blue")
canvas_baixista.pack(side=LEFT)

# Pianista
frame1_nivel_energia_pianista = Frame(frame1_nivel_energia, bg="white")
frame1_nivel_energia_pianista.pack(side=TOP, fill=BOTH, padx=5, pady=8)
label = tk.Label(frame1_nivel_energia_pianista, text="Pianista", width=7, font='Helvetica 10 bold')
label.pack(side=LEFT)
canvas_pianista = tk.Canvas(frame1_nivel_energia_pianista, height=30, bg="orange")
canvas_pianista.pack(side=LEFT)

# Desenha as barras segundo as energias enviadas como parâmetro
desenha_niveis_energia(200, 200, 200, 200)

# Label que representa as Batidas da Música
frame1_batidas = Frame(frame1, bg="white", width=100, height=40)
frame1_batidas.pack(side=TOP, fill=BOTH, padx=5, pady=15)

label_batidas = Label(frame1_batidas, text="BATIDA", width=7, font='Helvetica 10 bold')
label_batidas.pack(side=LEFT)
label_status_batida = Label(frame1_batidas, text="")
label_status_batida.pack(side=LEFT)

# Frame temporário para exibir niveis de energia em formato numérico
frame1_energias_numerico = Frame(frame1, bg="white", height=40)
frame1_energias_numerico.pack(side=TOP, fill=BOTH, padx=5, pady=5)

frame1_label_titulo_energia = Label(frame1_energias_numerico, text="Nivel Energia:", width=20, font='Helvetica 10 bold')
frame1_label_titulo_energia.pack(side=LEFT)

label_energia_numerico = Label(frame1_energias_numerico, text="", width=20, font='Helvetica 10 bold')
label_energia_numerico.pack(side=LEFT)

#exibe_status_batidas_sim()



''' Segundo Frame '''
frame2 = Frame(root, bg="black", width=200, height=400)
frame2.pack(side=LEFT, fill=BOTH, expand=True)

frame2_label_titulo = Label(frame2, text="CAIXA DE MÚSICA", fg="white", bg="black", font=("Helvetica", 16))
frame2_label_titulo.pack(pady=5)

frame2_cima = Frame(frame2, bg="black")
frame2_cima.pack(side=TOP, fill=BOTH, pady=5)

frame2_baixo = Frame(frame2, bg="black")
frame2_baixo.pack(side=TOP, fill=BOTH, expand=True)

# Criar "Caixa de Música": a Label da Playlist, onde ficarão as músicas disponíveis
caixa_musica = Listbox(frame2_cima, bg="white", fg="blue", width=50, selectbackground="black", selectforeground="green")
caixa_musica.pack()

# Criar controle deslizante (Slider) da posição da Música
slider_posicao = ttk.Scale(frame2_cima, from_=0, to=100, orient=HORIZONTAL, value=0, command=deslizar_posicao, length=360)
slider_posicao.pack(pady=5)

# Criar Barra de Status (momento atual e duração total) '''
barra_status = Label(frame2_cima, text="", bd=1, relief=GROOVE, anchor=W)
barra_status.pack()

# Criação imagens e definição dos comandos dos Botões do Player
frame2_baixo_botoes = Frame(frame2_baixo, bg="black")
frame2_baixo_botoes.pack(side=TOP, pady=5)

img_bt_anterior = redimensiona_imagem('botao_anterior.jpg', 30)
img_bt_proxima = redimensiona_imagem('botao_proxima.jpg', 30)
img_bt_play = redimensiona_imagem('botao_play.jpg', 40)
img_bt_pause = redimensiona_imagem('botao_pause.jpg', 35)
img_bt_stop = redimensiona_imagem('botao_stop.jpg', 30)

bt_anterior = Button(frame2_baixo_botoes, image=img_bt_anterior, borderwidth=0, command=anterior)
bt_proxima = Button(frame2_baixo_botoes, image=img_bt_proxima, borderwidth=0, command=proxima)
bt_play = Button(frame2_baixo_botoes, image=img_bt_play, borderwidth=0, command=tocar)
bt_pause = Button(frame2_baixo_botoes, image=img_bt_pause, borderwidth=0, command=pausar)
bt_stop = Button(frame2_baixo_botoes, image=img_bt_stop, borderwidth=0, command=parar)

bt_anterior.pack(side=LEFT, padx=5)
bt_stop.pack(side=LEFT, padx=5)
bt_play.pack(side=LEFT, padx=5)
bt_pause.pack(side=LEFT, padx=5)
bt_proxima.pack(side=LEFT, padx=5)

# Criar Label de texto para indicar qual música está tocando no momento '''
frame2_baixo_tocando = Frame(frame2_baixo, bg="black")
frame2_baixo_tocando.pack(side=TOP, fill=BOTH, expand=True)

texto_musica_tocando = Label(frame2_baixo_tocando, text="Música tocando:", bd=1, relief=GROOVE, anchor=W)
texto_musica_tocando.pack(pady=10)

###### adicionando o botão de separação ##########
botao_separador = tk.Button(frame2_baixo, text = "Separar o áudio", command=separate_file)
botao_separador.pack(pady = 10)



''' Terceiro Frame '''
frame3 = Frame(root, bg="black", width=200, height=400)
frame3.pack(side=LEFT, fill=BOTH, expand=True)

# Criar controle deslizante (Slider) do volume da Música '''
frame3_label_titulo = Label(frame3, text="VOLUME", fg="white", bg="black", font=("Helvetica", 16))
frame3_label_titulo.pack(pady=5)

slider_volume = ttk.Scale(frame3, from_=1, to=0, orient=VERTICAL, value=1, command=deslizar_volume, length=125)
slider_volume.pack(pady=5)



''' Menus '''
# Criar Menu do Player 
meu_menu = Menu(root)
root.config(menu=meu_menu)

# Criar Menu de Adição de Músicas 
menu_adiciona_musica = Menu(meu_menu)
meu_menu.add_cascade(label="Adicionar músicas", menu=menu_adiciona_musica)

# Criar opção de "adicionar uma música" ao Menu de Adição de Músicas 
menu_adiciona_musica.add_command(label="Adicione UMA música", command=adiciona_musica, font=('Helvetica', 14))

# Criar opção de "adicionar várias músicas" ao Menu de Adição de Músicas 
menu_adiciona_musica.add_command(label="Adicione VÁRIAS músicas à Playlist", command=adiciona_varias_musicas, font=('Helvetica', 14))

# Criar Menu de Deleção de Músicas 
menu_remover_musica = Menu(meu_menu)
meu_menu.add_cascade(label="Remover músicas", menu=menu_remover_musica)

# Criar opção de "deletar uma música" ao Menu de Deleção de Músicas 
menu_remover_musica.add_command(label="Deletar UMA música", command=deletar_musica, font=('Helvetica', 14))

# Criar opção de "deletar todas as músicas" ao Menu de Deleção de Músicas 
menu_remover_musica.add_command(label="Deletar TODAS as músicas", command=deletar_todas_musicas, font=('Helvetica', 14))



root.mainloop()