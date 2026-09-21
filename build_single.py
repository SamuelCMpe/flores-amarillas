"""Genera un HTML único con todo incrustado (GIFs, imágenes y fuente) para poder enviarlo solo.
Uso:  python build_single.py   ->  dist/index.html"""
import base64, os, re, urllib.request

OUT = 'dist/index.html'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36'
IMGS = ['img01.png','img02.png','img03.png','img04.gif','img05.gif','img06.png','img07.png',
        'img08.png','img09.png','img10.png']

def uri(path):
    mime = 'image/gif' if path.endswith('.gif') else 'image/png'
    return f'data:{mime};base64,' + base64.b64encode(open(path, 'rb').read()).decode()

def font_face():
    css = urllib.request.urlopen(urllib.request.Request(
        'https://fonts.googleapis.com/css2?family=Patrick+Hand&display=swap', headers={'User-Agent': UA})).read().decode()
    latin = re.search(r'/\* latin \*/\s*@font-face\s*\{.*?url\((.*?)\).*?unicode-range: (.*?);', css, re.S)
    woff = urllib.request.urlopen(urllib.request.Request(latin.group(1), headers={'User-Agent': UA})).read()
    return ("@font-face { font-family: 'Patrick Hand'; font-style: normal; font-weight: 400; font-display: swap;\n"
            f"    src: url(data:font/woff2;base64,{base64.b64encode(woff).decode()}) format('woff2');\n"
            f"    unicode-range: {latin.group(2)}; }}\n")

s = open('index.html', encoding='utf-8').read()

# 1) fuente: quita los <link> de Google Fonts y la incrusta
s, n = re.subn(r'<link rel="preconnect"[^>]*>\s*<link href="https://fonts\.googleapis\.com[^>]*>\s*', '', s)
assert n == 1, 'no encontré los <link> de la fuente'
s = s.replace('<style>\n', '<style>\n  ' + font_face(), 1)

# 2) conejo
assert 'src="assets/conejo.gif"' in s
s = s.replace('src="assets/conejo.gif"', f'src="{uri("assets/conejo.gif")}"', 1)

# 3) imágenes del viaje
pat = re.compile(r"const IMGS = \[.*?\]\.map\(n => 'assets/imagenes/' \+ n\);", re.S)
assert pat.search(s), 'no encontré IMGS'
lista = ',\n  '.join(f"'{uri('assets/imagenes/' + n)}'" for n in IMGS)
s = pat.sub(lambda m: f'const IMGS = [\n  {lista}\n];', s, count=1)

# 4) música
assert 'src="assets/musica.m4a"' in s
audio = 'data:audio/mp4;base64,' + base64.b64encode(open('assets/musica.m4a', 'rb').read()).decode()
s = s.replace('src="assets/musica.m4a"', f'src="{audio}"', 1)

os.makedirs('dist', exist_ok=True)
open(OUT, 'w', encoding='utf-8').write(s)
print(OUT, f'{len(s.encode())/1e6:.1f} MB')
