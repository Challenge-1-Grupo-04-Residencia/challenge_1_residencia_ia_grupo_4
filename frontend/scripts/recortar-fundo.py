"""Recorta o fundo das artes da Senhora Vera, preservando o traço preto.

As artes chegam de dois jeitos, e nenhum dos dois é transparente de verdade:

- **fundo escuro chapado**, como o retrato de mão no queixo;
- **xadrez de transparência desenhado**, como o retrato apontando — o programa
  que gerou a arte *pintou* o quadriculado cinza e branco na imagem.

Em nenhum dos dois dá para separar fundo de desenho comparando pixel a pixel.
No fundo escuro, o preto do fundo é o mesmo preto do contorno da arte: um
preenchimento por escuridão atravessa a linha do traço, entra pelo decote e
apaga o vestido florido, que também é preto.

Então a silhueta é fechada antes. O que é cor de desenho é dilatado e depois
contraído, o que costura por cima das linhas pretas e sela o contorno. O que
sobra de fora dessa silhueta selada, alcançável desde as bordas, é fundo; o que
ficou dentro — inclusive o preto do vestido — é desenho. No fim a máscara é
dilatada de novo, para devolver o contorno preto: a silhueta selada termina onde
começa a cor, e sem essa última dilatação a Vera sai recortada como adesivo, sem
a linha que a define.

Uso:

    uv run python frontend/scripts/recortar-fundo.py arte/origem.png public/saida.png
"""

import sys
from collections import deque

import numpy as np
from PIL import Image, ImageFilter

CLARO = 120    # no fundo escuro, acima disto o pixel é cor de desenho
LUZ_FUNDO = 200  # no fundo xadrez, abaixo disto o pixel é cor de desenho
CINZA = 14     # diferença entre canais que ainda conta como cinza de xadrez
COSTURA = 19        # janela do fecho: tem de ser maior que a espessura do traço
# Arte muito estampada precisa de janela maior: num vestido florido, o preto
# entre uma flor e outra se liga ao fundo por fora do contorno, e com a janela
# pequena o fecho não costura esse vão — o vestido sai esburacado.
TRACO = 13     # janela da dilatação que recupera o contorno preto da arte
LARGURA_MAXIMA = 1200


def mascara_de_desenho(pixels: np.ndarray) -> np.ndarray:
    """Marca o que é cor de desenho, escolhendo o critério pelo tipo de fundo."""
    rgb = pixels[:, :, :3].astype(np.int16)
    luz = rgb.max(axis=2)

    # Os quatro cantos dizem com que fundo estamos lidando: escuro chapado ou
    # xadrez claro. Olhar a imagem inteira não serviria — o vestido preto puxaria
    # a média para baixo em qualquer um dos dois casos; e a linha de cima também
    # não, porque o fundo escuro costuma vir com um brilho no meio, que levanta a
    # média e faz o programa escolher o critério errado. Canto é a parte do
    # quadro onde nunca há desenho.
    cantos = np.array([luz[:20, :20], luz[:20, -20:], luz[-20:, :20], luz[-20:, -20:]])
    if cantos.mean() < 60:
        return luz >= CLARO

    cinzento = (rgb.max(axis=2) - rgb.min(axis=2)) < CINZA
    return ~(cinzento & (luz > LUZ_FUNDO))


def _selar(desenho: np.ndarray, janela: int) -> np.ndarray:
    """Fecha o contorno: dilata as cores do desenho e contrai de volta."""
    selada = (
        Image.fromarray((desenho * 255).astype(np.uint8))
        .filter(ImageFilter.MaxFilter(janela))
        .filter(ImageFilter.MinFilter(janela))
    )
    return np.asarray(selada) > 127


def _preencher(partida: list, permitido: np.ndarray) -> np.ndarray:
    """Preenchimento por inundação dentro de `permitido`, a partir de `partida`."""
    alcancado = np.zeros_like(permitido)
    altura, largura = permitido.shape
    fila = deque(partida)
    while fila:
        y, x = fila.popleft()
        if alcancado[y, x] or not permitido[y, x]:
            continue
        alcancado[y, x] = True
        if y > 0:
            fila.append((y - 1, x))
        if y < altura - 1:
            fila.append((y + 1, x))
        if x > 0:
            fila.append((y, x - 1))
        if x < largura - 1:
            fila.append((y, x + 1))
    return alcancado


def _alcanca_a_borda(regiao: np.ndarray) -> np.ndarray:
    """As partes de `regiao` que encostam na borda da imagem."""
    altura, largura = regiao.shape
    partida = [(y, x) for x in range(largura) for y in (0, altura - 1) if regiao[y, x]]
    partida += [(y, x) for y in range(altura) for x in (0, largura - 1) if regiao[y, x]]
    return _preencher(partida, regiao)


def recortar(origem: str, destino: str) -> None:
    global COSTURA
    img = Image.open(origem).convert("RGBA")
    pixels = np.asarray(img)
    altura, largura = pixels.shape[:2]

    desenho = mascara_de_desenho(pixels)

    # Duas costuras, e não uma. A pequena acompanha o contorno de perto, mas não
    # fecha os vãos de uma estampa — num vestido florido, o preto entre as flores
    # se liga ao fundo e o vestido sai esburacado. A grande fecha a estampa, mas
    # cola no desenho qualquer fundo que encoste nele, como a parede atrás da
    # cabeça.
    #
    # Então usa-se a pequena para achar o fundo, e a grande só para **devolver**
    # o que ela recuperou e que não encosta na borda da imagem: estampa é ilha
    # no meio da figura; parede vai até o fim do quadro.
    dentro = _selar(desenho, COSTURA)

    fora = np.zeros_like(dentro)
    fila = deque()
    for x in range(largura):
        for y in (0, altura - 1):
            if not dentro[y, x]:
                fila.append((y, x))
    for y in range(altura):
        for x in (0, largura - 1):
            if not dentro[y, x]:
                fila.append((y, x))

    while fila:
        y, x = fila.popleft()
        if fora[y, x] or dentro[y, x]:
            continue
        fora[y, x] = True
        if y > 0:
            fila.append((y - 1, x))
        if y < altura - 1:
            fila.append((y + 1, x))
        if x > 0:
            fila.append((y, x - 1))
        if x < largura - 1:
            fila.append((y, x + 1))

    # Nota de limite, para quem vier depois: este recorte funciona com arte de
    # cor chapada sobre fundo liso. Estampa miúda sobre fundo escuro — um vestido
    # florido num estúdio preto — não sai limpa por aqui: o preto entre as flores
    # é o mesmo preto do fundo, e nenhuma das duas costuras separa os dois sem
    # estragar um ou outro. Nesse caso, use a arte como **cena de quadro inteiro**
    # em vez de recortá-la (ver `vera-estilo`).

    mascara = (
        Image.fromarray(((~fora) * 255).astype(np.uint8))
        .filter(ImageFilter.MaxFilter(TRACO))
        .filter(ImageFilter.GaussianBlur(1.0))
    )

    saida = pixels.copy()
    saida[:, :, 3] = np.asarray(mascara)

    recortada = Image.fromarray(saida, "RGBA")
    caixa = recortada.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
    recortada = recortada.crop(caixa)
    recortada.thumbnail((LARGURA_MAXIMA, LARGURA_MAXIMA), Image.LANCZOS)
    recortada.save(destino, optimize=True)
    print(f"{destino}: {recortada.size[0]}x{recortada.size[1]}")


if __name__ == "__main__":
    if len(sys.argv) > 3:
        COSTURA = int(sys.argv[3])
    recortar(sys.argv[1], sys.argv[2])
