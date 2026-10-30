
import pygame
import math
import random
import sys

pygame.init()

# CONFIGURACOES
LARGURA = 900
ALTURA = 700
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Asteroids")

RELOGIO = pygame.time.Clock()
FPS = 60

# CORES
PRETO = (8, 10, 20)
BRANCO = (240, 240, 240)
CINZA = (150, 155, 170)
AMARELO = (255, 220, 80)
VERMELHO = (255, 90, 90)

FONTE = pygame.font.SysFont("Arial", 25)
FONTE_GRANDE = pygame.font.SysFont("Arial", 65, bold=True)
FONTE_MEDIA = pygame.font.SysFont("Arial", 32)

# FISICA
ATRITO_NAVE = 0.992
ACELERACAO_NAVE = 0.16
VELOCIDADE_MAXIMA = 7
VELOCIDADE_TIRO = 9


def limitar_velocidade(vx, vy, limite):
    velocidade = math.hypot(vx, vy)

    if velocidade > limite:
        fator = limite / velocidade
        return vx * fator, vy * fator

    return vx, vy


def distancia(x1, y1, x2, y2):
    return math.hypot(x2 - x1, y2 - y1)


class Nave:
    def __init__(self):
        self.x = LARGURA / 2
        self.y = ALTURA / 2
        self.angulo = -90

        self.vx = 0
        self.vy = 0

        self.raio = 15
        self.tempo_protecao = 0

    def atualizar(self, teclas):

        # GIRAR: A ou SETA ESQUERDA
        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
            self.angulo -= 4

        # GIRAR: D ou SETA DIREITA
        if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
            self.angulo += 4

        radianos = math.radians(self.angulo)

        # ACELERAR PARA FRENTE: W ou SETA PARA CIMA
        if teclas[pygame.K_w] or teclas[pygame.K_UP]:
            self.vx += math.cos(radianos) * ACELERACAO_NAVE
            self.vy += math.sin(radianos) * ACELERACAO_NAVE

        # ACELERAR PARA TRAS: S ou SETA PARA BAIXO
        if teclas[pygame.K_s] or teclas[pygame.K_DOWN]:
            self.vx -= math.cos(radianos) * ACELERACAO_NAVE
            self.vy -= math.sin(radianos) * ACELERACAO_NAVE

        # LIMITAR VELOCIDADE
        self.vx, self.vy = limitar_velocidade(
            self.vx, self.vy, VELOCIDADE_MAXIMA
        )

        # INERCIA E ATRITO
        self.vx *= ATRITO_NAVE
        self.vy *= ATRITO_NAVE

        self.x += self.vx
        self.y += self.vy

        # ATRAVESSAR AS BORDAS
        self.x %= LARGURA
        self.y %= ALTURA

        if self.tempo_protecao > 0:
            self.tempo_protecao -= 1

    def desenhar(self):
        radianos = math.radians(self.angulo)

        frente = (
            self.x + math.cos(radianos) * 22,
            self.y + math.sin(radianos) * 22
        )

        esquerda = (
            self.x + math.cos(radianos + 2.5) * 17,
            self.y + math.sin(radianos + 2.5) * 17
        )

        direita = (
            self.x + math.cos(radianos - 2.5) * 17,
            self.y + math.sin(radianos - 2.5) * 17
        )

        pontos = [frente, esquerda, direita]

        if self.tempo_protecao == 0 or self.tempo_protecao % 10 < 5:
            pygame.draw.polygon(TELA, BRANCO, pontos, 2)

        # CHAMA DA PROPULSAO
        teclas = pygame.key.get_pressed()

        acelerando = (
            teclas[pygame.K_w]
            or teclas[pygame.K_UP]
        )

        if acelerando:
            chama = (
                self.x - math.cos(radianos) * 15,
                self.y - math.sin(radianos) * 15
            )

            pygame.draw.line(
                TELA,
                AMARELO,
                (self.x, self.y),
                chama,
                3
            )

    def reiniciar_posicao(self):
        self.x = LARGURA / 2
        self.y = ALTURA / 2
        self.angulo = -90
        self.vx = 0
        self.vy = 0
        self.tempo_protecao = 120


class Asteroide:
    def __init__(self, x=None, y=None, tamanho=3):
        self.tamanho = tamanho
        self.raio = tamanho * 13

        if x is None or y is None:
            while True:
                self.x = random.randint(0, LARGURA)
                self.y = random.randint(0, ALTURA)

                if distancia(
                    self.x, self.y,
                    nave.x, nave.y
                ) > 180:
                    break
        else:
            self.x = x
            self.y = y

        # VELOCIDADE E DIRECAO ALEATORIAS
        angulo = random.uniform(0, math.tau)
        velocidade = random.uniform(0.8, 2.0) * (4 / tamanho)

        self.vx = math.cos(angulo) * velocidade
        self.vy = math.sin(angulo) * velocidade

        # ROTACAO
        self.rotacao = random.uniform(0, 360)
        self.velocidade_rotacao = random.uniform(-1.8, 1.8)

        # MOVIMENTACAO IRREGULAR
        self.proxima_mudanca = random.randint(35, 120)
        self.direcao_extra = 0

        # FORMATO IRREGULAR INDIVIDUAL
        quantidade_pontos = random.randint(8, 12)
        self.formato = []

        for i in range(quantidade_pontos):
            angulo_ponto = (math.tau / quantidade_pontos) * i
            variacao = random.uniform(0.72, 1.25)

            px = math.cos(angulo_ponto) * self.raio * variacao
            py = math.sin(angulo_ponto) * self.raio * variacao

            self.formato.append((px, py))

    def atualizar(self, multiplicador):
        self.proxima_mudanca -= 1

        # MUDAR A TRAJETORIA DE FORMA ALEATORIA
        if self.proxima_mudanca <= 0:
            self.direcao_extra = random.uniform(-0.045, 0.045)
            self.proxima_mudanca = random.randint(35, 120)

        velocidade = math.hypot(self.vx, self.vy)

        if velocidade > 0:
            angulo = math.atan2(self.vy, self.vx)
            angulo += self.direcao_extra

            self.vx = math.cos(angulo) * velocidade
            self.vy = math.sin(angulo) * velocidade

        # MOVIMENTO
        self.x += self.vx * multiplicador
        self.y += self.vy * multiplicador

        # ROTACAO VISUAL
        self.rotacao += self.velocidade_rotacao

        # ATRAVESSAR AS BORDAS
        margem = self.raio + 5

        if self.x < -margem:
            self.x = LARGURA + margem
        elif self.x > LARGURA + margem:
            self.x = -margem

        if self.y < -margem:
            self.y = ALTURA + margem
        elif self.y > ALTURA + margem:
            self.y = -margem

    def desenhar(self):
        pontos = []
        radianos = math.radians(self.rotacao)

        for px, py in self.formato:
            x_rotacionado = (
                px * math.cos(radianos)
                - py * math.sin(radianos)
            )

            y_rotacionado = (
                px * math.sin(radianos)
                + py * math.cos(radianos)
            )

            pontos.append((
                self.x + x_rotacionado,
                self.y + y_rotacionado
            ))

        pygame.draw.polygon(TELA, CINZA, pontos, 2)


class Tiro:
    def __init__(self, x, y, angulo):
        self.x = x
        self.y = y

        radianos = math.radians(angulo)

        self.vx = math.cos(radianos) * VELOCIDADE_TIRO
        self.vy = math.sin(radianos) * VELOCIDADE_TIRO

        self.tempo = 65

    def atualizar(self):
        self.x += self.vx
        self.y += self.vy

        self.x %= LARGURA
        self.y %= ALTURA

        self.tempo -= 1

    def desenhar(self):
        pygame.draw.circle(
            TELA,
            AMARELO,
            (int(self.x), int(self.y)),
            3
        )


def criar_fragmentos(asteroide):
    fragmentos = []

    if asteroide.tamanho > 1:
        for _ in range(2):
            novo = Asteroide(
                asteroide.x,
                asteroide.y,
                asteroide.tamanho - 1
            )

            angulo = random.uniform(0, math.tau)
            velocidade = random.uniform(1.5, 3.5)

            novo.vx += math.cos(angulo) * velocidade
            novo.vy += math.sin(angulo) * velocidade

            fragmentos.append(novo)

    return fragmentos


def reiniciar():
    global nave, asteroides, tiros
    global pontuacao, vidas, multiplicador_velocidade
    global ultimo_aumento, jogo_acabou

    nave = Nave()

    asteroides = [
        Asteroide(tamanho=3)
        for _ in range(5)
    ]

    tiros = []
    pontuacao = 0
    vidas = 3

    multiplicador_velocidade = 1.0
    ultimo_aumento = pygame.time.get_ticks()

    jogo_acabou = False


# INICIAR JOGO
reiniciar()

executando = True

while executando:
    RELOGIO.tick(FPS)
    TELA.fill(PRETO)

    # EVENTOS
    for evento in pygame.event.get():

        if evento.type == pygame.QUIT:
            executando = False

        if evento.type == pygame.KEYDOWN:

            if not jogo_acabou:
                if evento.key == pygame.K_SPACE:
                    radianos = math.radians(nave.angulo)

                    tiro_x = nave.x + math.cos(radianos) * 22
                    tiro_y = nave.y + math.sin(radianos) * 22

                    tiros.append(
                        Tiro(tiro_x, tiro_y, nave.angulo)
                    )

            else:
                if evento.key == pygame.K_RETURN:
                    reiniciar()

    teclas = pygame.key.get_pressed()

    if not jogo_acabou:

        # AUMENTAR VELOCIDADE A CADA 5 SEGUNDOS
        agora = pygame.time.get_ticks()

        if agora - ultimo_aumento >= 5000:
            multiplicador_velocidade *= 1.2
            ultimo_aumento = agora

        # ATUALIZAR NAVE
        nave.atualizar(teclas)

        # ATUALIZAR ASTEROIDES
        for asteroide in asteroides:
            asteroide.atualizar(multiplicador_velocidade)

        # ATUALIZAR TIROS
        for tiro in tiros[:]:
            tiro.atualizar()

            if tiro.tempo <= 0:
                tiros.remove(tiro)

        # COLISAO DOS TIROS COM ASTEROIDES
        for tiro in tiros[:]:
            for asteroide in asteroides[:]:

                if distancia(
                    tiro.x, tiro.y,
                    asteroide.x, asteroide.y
                ) < asteroide.raio:

                    if tiro in tiros:
                        tiros.remove(tiro)

                    if asteroide in asteroides:
                        asteroides.remove(asteroide)

                    pontuacao += asteroide.tamanho * 10

                    asteroides.extend(
                        criar_fragmentos(asteroide)
                    )

                    break

        # COLISAO DA NAVE COM ASTEROIDES
        if nave.tempo_protecao == 0:
            for asteroide in asteroides[:]:

                if distancia(
                    nave.x, nave.y,
                    asteroide.x, asteroide.y
                ) < asteroide.raio + nave.raio:

                    asteroides.remove(asteroide)

                    vidas -= 1
                    nave.reiniciar_posicao()

                    if vidas <= 0:
                        jogo_acabou = True

                    break

        # CRIAR NOVOS ASTEROIDES SE TODOS FOREM DESTRUIDOS
        if len(asteroides) == 0:
            asteroides = [
                Asteroide(tamanho=3)
                for _ in range(5)
            ]

        # DESENHAR ELEMENTOS
        nave.desenhar()

        for asteroide in asteroides:
            asteroide.desenhar()

        for tiro in tiros:
            tiro.desenhar()

    else:
        # GAME OVER
        texto_game_over = FONTE_GRANDE.render(
            "GAME OVER", True, VERMELHO
        )

        texto_pontuacao = FONTE_MEDIA.render(
            f"Pontuacao final: {pontuacao}",
            True,
            BRANCO
        )

        texto_reiniciar = FONTE.render(
            "Pressione ENTER para jogar novamente",
            True,
            BRANCO
        )

        TELA.blit(
            texto_game_over,
            texto_game_over.get_rect(
                center=(LARGURA / 2, ALTURA / 2 - 65)
            )
        )

        TELA.blit(
            texto_pontuacao,
            texto_pontuacao.get_rect(
                center=(LARGURA / 2, ALTURA / 2 + 10)
            )
        )

        TELA.blit(
            texto_reiniciar,
            texto_reiniciar.get_rect(
                center=(LARGURA / 2, ALTURA / 2 + 65)
            )
        )

    # INTERFACE
    texto_pontos = FONTE.render(
        f"Pontuacao: {pontuacao}", True, BRANCO
    )

    texto_vidas = FONTE.render(
        f"Vidas: {vidas}", True, BRANCO
    )

    texto_velocidade = FONTE.render(
        f"Velocidade: {multiplicador_velocidade:.1f}x",
        True,
        BRANCO
    )

    TELA.blit(texto_pontos, (20, 15))
    TELA.blit(texto_vidas, (20, 45))
    TELA.blit(texto_velocidade, (20, 75))

    controles = FONTE.render(
        "SETAS ou WASD: CONTROLAR | ESPACO: ATIRAR",
        True,
        CINZA
    )

    TELA.blit(
        controles,
        controles.get_rect(
            center=(LARGURA / 2, ALTURA - 25)
        )
    )

    pygame.display.flip()

pygame.quit()
sys.exit()
