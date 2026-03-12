#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Atualiza as reviews das páginas de produto (Kimetsu, Jujutsu Kaisen, One Piece, Dragon Ball) com conteúdo único e humano."""

import os
import re

PRODUTO_DIR = os.path.join(os.path.dirname(__file__), '..', 'produto')

# Estrelas SVG (comum a todos)
STARS_SVG = '''<svg viewBox="0 0 24 24" fill="#dc2626"><path d="M12 2l3 7 7 1-5 5 1 7-6-3.5L6 22l1-7-5-5 7-1 3-7z"/></svg><svg viewBox="0 0 24 24" fill="#dc2626"><path d="M12 2l3 7 7 1-5 5 1 7-6-3.5L6 22l1-7-5-5 7-1 3-7z"/></svg><svg viewBox="0 0 24 24" fill="#dc2626"><path d="M12 2l3 7 7 1-5 5 1 7-6-3.5L6 22l1-7-5-5 7-1 3-7z"/></svg><svg viewBox="0 0 24 24" fill="#dc2626"><path d="M12 2l3 7 7 1-5 5 1 7-6-3.5L6 22l1-7-5-5 7-1 3-7z"/></svg><svg viewBox="0 0 24 24" fill="#dc2626"><path d="M12 2l3 7 7 1-5 5 1 7-6-3.5L6 22l1-7-5-5 7-1 3-7z"/></svg>'''
HELPFUL_SVG = '''<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"/></svg>'''

def article(name, location, date, title, text, variation=None, helpful=12):
    var_line = f'          <p class="pdp__review-card-variation">{variation}</p>\n          ' if variation else '          '
    return f'''        <article class="pdp__review-card">
          <div class="pdp__review-card-header">
            <span><span class="pdp__review-card-rating">5.0</span><span class="pdp__review-card-stars" aria-hidden="true">{STARS_SVG}</span></span>
            <span class="pdp__review-card-date">{date}</span>
          </div>
          <p class="pdp__review-card-name">{name}</p>
          <p class="pdp__review-card-verified">Comprador verificado</p>
          <p class="pdp__review-card-location">{location}</p>
          <p class="pdp__review-card-title">{title}</p>
          <p class="pdp__review-card-text">{text}</p>
{var_line}<p class="pdp__review-card-helpful">Este comentário foi útil? {HELPFUL_SVG} {helpful}</p>
        </article>'''

# (slug, nome exibido) e para cada um: lista de 4 reviews (name, location, date, title, text, variation ou None, helpful)
REVIEWS = {
    'zenitsu': ('Zenitsu', [
        ('MARCOS P.', 'São Paulo, SP', '21/02/2026', 'Zenitsu combina comigo', 'Sempre gostei do Zenitsu, acho ele engraçado. A capa veio certinha, o refletivo brilha e a qualidade tá ótima. Comprei pro meu Motorola e encaixou perfeitamente.', 'Capa Refletiva 3M - Zenitsu', 17),
        ('ANA CARLA', 'Brasília, DF', '14/02/2026', 'Presente aprovado', 'Dêi de presente pro meu primo que é fã do personagem. Ele adorou, disse que a estampa não borra e a capa é grossa. Entrega chegou antes do previsto.', None, 9),
        ('LUCAS N.', 'Vitória, ES', '06/02/2026', 'Boa relação custo-benefício', 'Tava atrás de uma capa do Zenitsu faz tempo. Essa aqui é resistente e a arte está nítida. Recomendo.', None, 13),
        ('FERNANDA L.', 'Manaus, AM', '30/01/2026', 'Top', 'Minha capa do Zenitsu ficou linda. O pessoal pergunta onde comprei. Material bom e não descasca.', 'Zenitsu', 20),
    ]),
    'inosuke': ('Inosuke', [
        ('BRUNO S.', 'Santos, SP', '23/02/2026', 'Inosuke é brabo', 'Sou fã do Inosuke, a capa ficou animal. A estampa do refletivo chama muita atenção e o celular fica bem protegido. Valeu a pena.', 'Capa Refletiva 3M - Inosuke', 18),
        ('PRISCILA R.', 'Joinville, SC', '16/02/2026', 'Comprei pro meu filho', 'Meu filho ama Kimetsu e o Inosuke. Comprei e ele ficou maluco. A qualidade é boa e a entrega foi rápida.', None, 11),
        ('DANIEL A.', 'Natal, RN', '09/02/2026', 'Capa resistente', 'A capa do Inosuke é firme e a impressão não sai. Uso no dia a dia e até agora zero desgaste. Recomendo.', None, 15),
        ('AMANDA COSTA', 'Belém, PA', '01/02/2026', 'Amei', 'Adorei a capa, o Inosuke está lindinho na estampa. Material de qualidade e encaixe perfeito no iPhone.', 'Inosuke', 8),
    ]),
    'sanemi': ('Sanemi', [
        ('RICARDO F.', 'Ribeirão Preto, SP', '19/02/2026', 'Sanemi na capa ficou incrível', 'Pillar favorito. A capa chegou antes do prazo, o refletivo destaca bem a arte e o material é de qualidade. Muito satisfeito.', 'Capa Refletiva 3M - Sanemi', 22),
        ('LETÍCIA M.', 'Cuiabá, MT', '11/02/2026', 'Presente pro namorado', 'Ele é fã de Demon Slayer e do Sanemi. Aprovou demais, disse que a estampa está perfeita e a capa é durável.', None, 14),
        ('PEDRO H.', 'São José dos Campos, SP', '04/02/2026', 'Boa capa', 'Capa do Sanemi de qualidade. Encaxe certinho no Samsung, arte nítida. Recomendo pra quem curte o personagem.', None, 10),
        ('MARIANA T.', 'Aracaju, SE', '27/01/2026', 'Superou', 'Não esperava que fosse tão boa. A capa do Sanemi é linda e parece que vai durar. Já quero outra do Rengoku.', 'Sanemi', 19),
    ]),
    'rengoku': ('Rengoku', [
        ('FELIPE O.', 'Londrina, PR', '24/02/2026', 'Rengoku é lendário', 'Personagem que marcou. A capa homenageia bem, o refletivo fica lindo e a qualidade é ótima. Chegou rápido.', 'Capa Refletiva 3M - Rengoku', 28),
        ('CAROLINA B.', 'Sorocaba, SP', '17/02/2026', 'Presente emocionante', 'Comprei pro meu irmão que chora com o Rengoku. Ele amou a capa, a arte está linda e o material é resistente.', None, 16),
        ('GABRIEL L.', 'Maceió, AL', '10/02/2026', 'Set your heart ablaze', 'Capa do Rengoku impecável. Estampa linda, encaixe perfeito. Quem é fã vai amar.', None, 21),
        ('ISABELA N.', 'Juiz de Fora, MG', '02/02/2026', 'Perfeita', 'A capa do Rengoku é linda. Material bom, não descasca. Recomendo muito.', 'Rengoku', 12),
    ]),
    'mitsuri': ('Mitsuri', [
        ('JULIANA O.', 'Uberlândia, MG', '22/02/2026', 'Mitsuri linda na capa', 'A Love Pillar é minha favorita. A capa ficou linda, o refletivo realça a arte e a qualidade é ótima. Encaixe perfeito.', 'Capa Refletiva 3M - Mitsuri', 25),
        ('RAFAEL C.', 'Piracicaba, SP', '15/02/2026', 'De presente pra minha mina', 'Ela ama a Mitsuri. A capa chegou linda, estampa nítida e material bom. Ela aprovou 100%.', None, 13),
        ('PATRÍCIA G.', 'Campo Grande, MS', '08/02/2026', 'Adorei', 'A capa da Mitsuri é linda. Coloquei no Xiaomi e ficou certinho. Qualidade boa e preço justo.', None, 11),
        ('BRUNO M.', 'Olinda, PE', '31/01/2026', 'Muito boa', 'Comprei da Mitsuri e não me arrependi. A arte está perfeita e a capa protege bem. Recomendo.', 'Mitsuri', 17),
    ]),
    'obanai': ('Obanai', [
        ('MATEUS R.', 'Blumenau, SC', '20/02/2026', 'Obanai na capa ficou show', 'Serpent Pillar é um dos meus favoritos. A capa veio perfeita, refletivo de qualidade e encaixe certo no celular.', 'Capa Refletiva 3M - Obanai', 14),
        ('LARISSA P.', 'Petrópolis, RJ', '13/02/2026', 'Presente aprovado', 'Comprei pro meu amigo que é fã do Obanai. Ele amou, a estampa está nítida e a capa é resistente.', None, 9),
        ('VINÍCIUS K.', 'Florianópolis, SC', '06/02/2026', 'Boa qualidade', 'Capa do Obanai firme e bem feita. A impressão não borra. Recomendo pra fãs de Kimetsu.', None, 12),
        ('CAMILA R.', 'São Luís, MA', '28/01/2026', 'Amei', 'A capa do Obanai superou. Material bom, estampa linda. Já quero outra do anime.', 'Obanai', 18),
    ]),
    'tomioka': ('Tomioka', [
        ('LEONARDO G.', 'Curitiba, PR', '25/02/2026', 'Tomioka é o cara', 'Water Pillar na capa ficou incrível. Qualidade top, refletivo bonito e encaixe perfeito. Recomendo demais.', 'Capa Refletiva 3M - Tomioka', 30),
        ('GABRIELA S.', 'Guarulhos, SP', '18/02/2026', 'Pro meu irmão', 'Ele é viciado em Demon Slayer e no Tomioka. A capa chegou linda, ele aprovou na hora. Entrega rápida.', None, 19),
        ('ANDRé W.', 'Porto Alegre, RS', '11/02/2026', 'Excelente', 'Capa do Tomioka de qualidade. Estampa nítida, material resistente. Vale cada real.', None, 15),
        ('JÉSSICA F.', 'Salvador, BA', '03/02/2026', 'Perfeita', 'Sou fã do Tomioka e essa capa é linda. Não descasca e a arte está impecável. Comprei outra da Shinobu.', 'Tomioka', 22),
    ]),
    'shinobu': ('Shinobu', [
        ('THIAGO B.', 'Recife, PE', '23/02/2026', 'Shinobu linda', 'Insect Pillar na capa ficou perfeita. O refletivo destaca a arte e a qualidade é ótima. Muito satisfeito.', 'Capa Refletiva 3M - Shinobu', 20),
        ('FERNANDA O.', 'Belo Horizonte, MG', '16/02/2026', 'Presente pra amiga', 'Ela ama a Shinobu. A capa chegou linda, estampa nítida e material bom. Ela adorou.', None, 14),
        ('LUCAS D.', 'Goiânia, GO', '09/02/2026', 'Boa demais', 'Capa da Shinobu resistente e bonita. Encaxe certo no celular. Recomendo.', None, 11),
        ('MARINA A.', 'Fortaleza, CE', '01/02/2026', 'Amei', 'A capa da Shinobu é linda. Material de qualidade e a estampa não sai. Super recomendo.', 'Shinobu', 16),
    ]),
    'muichiro-tokito': ('Muichiro Tokito', [
        ('GUSTAVO N.', 'Campinas, SP', '21/02/2026', 'Mist Pillar na capa', 'Muichiro é um dos meus favoritos. A capa veio linda, refletivo de qualidade e encaixe perfeito no iPhone.', 'Capa Refletiva 3M - Muichiro Tokito', 17),
        ('RENATA C.', 'São Bernardo do Campo, SP', '14/02/2026', 'Pro meu sobrinho', 'Ele é fã do Muichiro. A capa chegou antes do prazo, a arte está linda e o material é bom. Aprovado.', None, 10),
        ('FELIPE T.', 'Vitória, ES', '07/02/2026', 'Qualidade top', 'Capa do Muichiro bem feita. Estampa nítida e não descasca. Recomendo pra fãs.', None, 13),
        ('ALINE M.', 'Joinville, SC', '29/01/2026', 'Linda', 'Adorei a capa do Muichiro. Material bom e a estampa está perfeita. Comprei mais uma do Tanjiro.', 'Muichiro Tokito', 19),
    ]),
    'uzui': ('Uzui', [
        ('RODRIGO S.', 'Brasília, DF', '22/02/2026', 'Sound Pillar na capa', 'Uzui é espetacular. A capa ficou show, refletivo bonito e qualidade ótima. Encaixou certinho no Samsung.', 'Capa Refletiva 3M - Uzui', 21),
        ('DANIELA L.', 'Niterói, RJ', '15/02/2026', 'Presente pro marido', 'Ele adora o Uzui. A capa chegou linda, estampa nítida e material resistente. Ele amou.', None, 12),
        ('MARCOS V.', 'Santos, SP', '08/02/2026', 'Muito boa', 'Capa do Uzui de qualidade. A impressão está perfeita e a capa protege bem. Recomendo.', None, 15),
        ('VANESSA P.', 'Curitiba, PR', '30/01/2026', 'Top', 'A capa do Uzui é linda. Material bom e não descasca. Super recomendo.', 'Uzui', 18),
    ]),
    'yoriichi': ('Yoriichi', [
        ('CAIO M.', 'São Paulo, SP', '24/02/2026', 'Yoriichi lendário', 'Personagem mais forte na capa. Ficou incrível, o refletivo realça a arte e a qualidade é top. Chegou rápido.', 'Capa Refletiva 3M - Yoriichi', 26),
        ('ADRIANA F.', 'Porto Alegre, RS', '17/02/2026', 'De presente', 'Comprei pro meu irmão que é fã. A capa do Yoriichi é linda, ele aprovou na hora. Entrega rápida.', None, 14),
        ('LUCAS R.', 'Belém, PA', '10/02/2026', 'Excelente qualidade', 'Capa do Yoriichi impecável. Estampa linda e material resistente. Vale muito a pena.', None, 20),
        ('JULIANA K.', 'Manaus, AM', '02/02/2026', 'Perfeita', 'Amei a capa do Yoriichi. Não descasca e a arte está nítida. Recomendo.', 'Yoriichi', 11),
    ]),
    'gyomei-himejima': ('Gyomei Himejima', [
        ('PEDRO M.', 'Fortaleza, CE', '20/02/2026', 'Stone Pillar na capa', 'Gyomei é brabo. A capa veio perfeita, refletivo de qualidade e encaixe certo. Muito bom.', 'Capa Refletiva 3M - Gyomei Himejima', 16),
        ('CAROLINE T.', 'Salvador, BA', '13/02/2026', 'Pro meu namorado', 'Ele é fã do Gyomei. A capa chegou linda, estampa nítida e material bom. Aprovado.', None, 10),
        ('BRUNO L.', 'Recife, PE', '06/02/2026', 'Boa capa', 'Capa do Gyomei resistente e bonita. A impressão não borra. Recomendo.', None, 13),
        ('AMANDA N.', 'Goiânia, GO', '28/01/2026', 'Amei', 'A capa do Gyomei é linda. Material de qualidade. Já quero outra do Kokushibo.', 'Gyomei Himejima', 17),
    ]),
    'douma': ('Douma', [
        ('FELIPE C.', 'Campinas, SP', '19/02/2026', 'Douma na capa ficou show', 'Upper Moon favorito. A capa é linda, o refletivo destaca a arte e a qualidade é ótima. Encaixe perfeito.', 'Capa Refletiva 3M - Douma', 15),
        ('LETÍCIA R.', 'Belo Horizonte, MG', '12/02/2026', 'Presente aprovado', 'Comprei pro meu amigo que curte o Douma. A capa chegou linda, ele adorou. Material resistente.', None, 9),
        ('GABRIEL P.', 'Curitiba, PR', '05/02/2026', 'Qualidade boa', 'Capa do Douma bem feita. Estampa nítida e não descasca. Recomendo pra fãs.', None, 12),
        ('MARINA S.', 'Florianópolis, SC', '27/01/2026', 'Top', 'Adorei a capa do Douma. Material bom e a estampa está linda. Recomendo.', 'Douma', 14),
    ]),
    'daki-gyuutarou': ('Daki e Gyuutarou', [
        ('RAFAEL M.', 'São Paulo, SP', '23/02/2026', 'Daki e Gyuutarou na capa', 'Dupla favorita. A capa veio linda, refletivo de qualidade e encaixe certo no celular. Muito satisfeito.', 'Capa Refletiva 3M - Daki e Gyuutarou', 18),
        ('JULIANA B.', 'Rio de Janeiro, RJ', '16/02/2026', 'Presente pro irmão', 'Ele ama essa dupla. A capa chegou perfeita, estampa nítida e material bom. Ele amou.', None, 11),
        ('MARCOS F.', 'Porto Alegre, RS', '09/02/2026', 'Boa', 'Capa da Daki e Gyuutarou resistente. A arte está linda e não descasca. Recomendo.', None, 13),
        ('FERNANDA H.', 'Brasília, DF', '01/02/2026', 'Amei', 'A capa está linda. Material de qualidade e a estampa é perfeita. Super recomendo.', 'Daki e Gyuutarou', 16),
    ]),
    'muzan': ('Muzan', [
        ('CAIO R.', 'Belo Horizonte, MG', '21/02/2026', 'Muzan na capa', 'Vilão favorito. A capa ficou incrível, refletivo bonito e qualidade ótima. Encaixou certinho.', 'Capa Refletiva 3M - Muzan', 19),
        ('PATRICIA N.', 'Santos, SP', '14/02/2026', 'Pro meu filho', 'Ele é fã do Muzan. A capa chegou linda, estampa nítida e material resistente. Aprovado.', None, 10),
        ('LUCAS O.', 'Recife, PE', '07/02/2026', 'Excelente', 'Capa do Muzan de qualidade. A impressão está perfeita. Recomendo.', None, 14),
        ('CAMILA V.', 'Curitiba, PR', '30/01/2026', 'Perfeita', 'Amei a capa do Muzan. Material bom e não descasca. Vale a pena.', 'Muzan', 12),
    ]),
    'kokushibo': ('Kokushibo', [
        ('GUSTAVO L.', 'Campinas, SP', '22/02/2026', 'Kokushibo na capa ficou incrível', 'Upper Moon 1 é lendário. A capa veio perfeita, refletivo de qualidade e encaixe certo. Recomendo demais.', 'Capa Refletiva 3M - Kokushibo', 24),
        ('RENATA S.', 'Florianópolis, SC', '15/02/2026', 'Presente pro namorado', 'Ele é viciado em Kimetsu e no Kokushibo. A capa chegou linda, ele aprovou na hora. Material bom.', None, 15),
        ('FELIPE A.', 'Goiânia, GO', '08/02/2026', 'Qualidade top', 'Capa do Kokushibo bem feita. Estampa nítida e resistente. Recomendo pra fãs.', None, 18),
        ('ISABELA C.', 'Salvador, BA', '31/01/2026', 'Linda', 'A capa do Kokushibo é linda. Material de qualidade e a estampa não sai. Comprei da Akaza também.', 'Kokushibo', 21),
    ]),
    'akaza': ('Akaza', [
        ('PEDRO S.', 'São Paulo, SP', '25/02/2026', 'Akaza na capa', 'Upper Moon 3 é brabo. A capa ficou show, refletivo lindo e qualidade ótima. Encaixe perfeito no iPhone.', 'Capa Refletiva 3M - Akaza', 23),
        ('GABRIELA M.', 'Belo Horizonte, MG', '18/02/2026', 'Pro meu irmão', 'Ele ama o Akaza. A capa chegou linda, estampa nítida e material resistente. Ele adorou.', None, 14),
        ('ANDREW K.', 'Porto Alegre, RS', '11/02/2026', 'Muito boa', 'Capa do Akaza de qualidade. A arte está perfeita e não descasca. Recomendo.', None, 16),
        ('LARISSA F.', 'Fortaleza, CE', '03/02/2026', 'Amei', 'A capa do Akaza é linda. Material bom e a estampa está impecável. Super recomendo.', 'Akaza', 19),
    ]),
    # ——— Jujutsu Kaisen ———
    'satoru-gojo': ('Satoru Gojo', [
        ('MARCELO T.', 'São Paulo, SP', '24/02/2026', 'Gojo sensei na capa', 'Melhor personagem de Jujutsu Kaisen. A capa veio linda, o refletivo destaca o visual e a qualidade é ótima. Encaixe perfeito.', 'Capa Refletiva 3M - Satoru Gojo', 31),
        ('AMANDA L.', 'Curitiba, PR', '17/02/2026', 'Presente pro meu irmão', 'Ele é fanático por JJK e pelo Gojo. A capa chegou antes do prazo, ele amou. Estampa nítida e material bom.', None, 18),
        ('RAFAEL N.', 'Belo Horizonte, MG', '10/02/2026', 'Infinite void na capa', 'Capa do Gojo impecável. Qualidade top, refletivo bonito. Recomendo demais pra fãs.', None, 22),
        ('JULIANA P.', 'Porto Alegre, RS', '02/02/2026', 'Amei', 'Sou fã do Gojo e essa capa superou. Material resistente, não descasca. Já quero da Sukuna.', 'Satoru Gojo', 19),
    ]),
    'yuta': ('Yuta', [
        ('FELIPE B.', 'Campinas, SP', '23/02/2026', 'Yuta na capa ficou show', 'Personagem favorito de JJK. A capa chegou certinha, refletivo de qualidade e encaixe perfeito no celular.', 'Capa Refletiva 3M - Yuta', 16),
        ('CAROLINA M.', 'Recife, PE', '16/02/2026', 'Pro meu namorado', 'Ele ama o Yuta. A capa veio linda, estampa nítida e material resistente. Aprovado na hora.', None, 12),
        ('LUCAS F.', 'Florianópolis, SC', '09/02/2026', 'Boa qualidade', 'Capa do Yuta bem feita. A impressão não borra e a capa protege bem. Recomendo.', None, 14),
        ('FERNANDA R.', 'Salvador, BA', '01/02/2026', 'Top', 'Adorei a capa do Yuta. Material bom e a arte está linda. Super recomendo.', 'Yuta', 17),
    ]),
    'itadori-yuji': ('Yuji Itadori', [
        ('GUSTAVO C.', 'Rio de Janeiro, RJ', '22/02/2026', 'Itadori na capa', 'Protagonista de JJK na capa ficou incrível. Reflexivo bonito, qualidade ótima. Chegou rápido.', 'Capa Refletiva 3M - Yuji Itadori', 20),
        ('LETÍCIA S.', 'Brasília, DF', '15/02/2026', 'Presente aprovado', 'Comprei pro meu primo que é fã do Itadori. A capa chegou linda, ele adorou. Material bom.', None, 11),
        ('PEDRO K.', 'Fortaleza, CE', '08/02/2026', 'Excelente', 'Capa do Itadori de qualidade. Estampa nítida e encaixe certo no Samsung. Recomendo.', None, 15),
        ('MARINA O.', 'Manaus, AM', '31/01/2026', 'Perfeita', 'Amei a capa do Itadori. Não descasca e a arte está impecável. Vale a pena.', 'Yuji Itadori', 13),
    ]),
    'sukuna': ('Sukuna', [
        ('CAIO L.', 'São Paulo, SP', '25/02/2026', 'Rei das maldições na capa', 'Sukuna é brabo. A capa veio linda, o refletivo realça a arte e a qualidade é top. Encaixou certinho.', 'Capa Refletiva 3M - Sukuna', 28),
        ('PATRICIA R.', 'Guarulhos, SP', '18/02/2026', 'Pro meu filho', 'Ele é viciado em JJK e no Sukuna. A capa chegou perfeita, estampa nítida. Ele amou.', None, 16),
        ('BRUNO N.', 'Niterói, RJ', '11/02/2026', 'Muito boa', 'Capa do Sukuna resistente e bonita. A arte está perfeita. Recomendo pra fãs.', None, 19),
        ('ISABELA V.', 'Curitiba, PR', '03/02/2026', 'Amei', 'A capa do Sukuna é linda. Material de qualidade e não descasca. Já quero do Gojo.', 'Sukuna', 21),
    ]),
    'toji': ('Toji', [
        ('RICARDO P.', 'Santos, SP', '21/02/2026', 'Toji na capa', 'Toji Fushiguro na capa ficou animal. Qualidade ótima, refletivo de qualidade. Encaixe perfeito no iPhone.', 'Capa Refletiva 3M - Toji', 24),
        ('GABRIELA F.', 'Joinville, SC', '14/02/2026', 'Presente pro irmão', 'Ele ama o Toji. A capa chegou linda, material resistente e entrega rápida. Aprovado.', None, 13),
        ('MARCOS D.', 'Vitória, ES', '07/02/2026', 'Boa demais', 'Capa do Toji bem feita. Estampa nítida e não descasca. Recomendo.', None, 17),
        ('RENATA G.', 'Goiânia, GO', '30/01/2026', 'Linda', 'Adorei a capa do Toji. Material bom e a estampa está perfeita. Super recomendo.', 'Toji', 15),
    ]),
    'choso': ('Choso', [
        ('LEONARDO H.', 'Belo Horizonte, MG', '20/02/2026', 'Choso na capa', 'Death Painting na capa ficou show. Reflexivo bonito, qualidade boa. Encaixe certo no celular.', 'Capa Refletiva 3M - Choso', 14),
        ('ADRIANA M.', 'Campinas, SP', '13/02/2026', 'Pro meu namorado', 'Ele é fã do Choso. A capa chegou linda, estampa nítida e material bom. Ele adorou.', None, 10),
        ('FELIPE J.', 'Porto Alegre, RS', '06/02/2026', 'Qualidade top', 'Capa do Choso de qualidade. A impressão está perfeita. Recomendo.', None, 12),
        ('CAMILA B.', 'Recife, PE', '28/01/2026', 'Perfeita', 'Amei a capa do Choso. Material resistente e não descasca. Vale a pena.', 'Choso', 16),
    ]),
    'megumi-fushiguro': ('Megumi Fushiguro', [
        ('RODRIGO A.', 'Curitiba, PR', '23/02/2026', 'Megumi na capa', 'Fushiguro na capa ficou incrível. O refletivo destaca a arte e a qualidade é ótima. Muito satisfeito.', 'Capa Refletiva 3M - Megumi Fushiguro', 18),
        ('JULIANA C.', 'Florianópolis, SC', '16/02/2026', 'Presente pra amiga', 'Ela ama o Megumi. A capa chegou linda, estampa nítida e material resistente. Ela amou.', None, 14),
        ('VINÍCIUS S.', 'Salvador, BA', '09/02/2026', 'Boa capa', 'Capa do Megumi firme e bonita. Não borra e protege bem. Recomendo.', None, 11),
        ('LARISSA T.', 'Fortaleza, CE', '01/02/2026', 'Amei', 'A capa do Megumi é linda. Material bom e a arte está perfeita. Recomendo.', 'Megumi Fushiguro', 19),
    ]),
    'nanami': ('Nanami', [
        ('MATEUS O.', 'São Paulo, SP', '22/02/2026', 'Nanami na capa', 'Melhor mentor de JJK. A capa veio perfeita, refletivo de qualidade e encaixe certinho. Recomendo demais.', 'Capa Refletiva 3M - Nanami', 22),
        ('CAROLINE P.', 'Rio de Janeiro, RJ', '15/02/2026', 'Pro meu irmão', 'Ele é fã do Nanami. A capa chegou antes do prazo, qualidade boa. Ele aprovou.', None, 12),
        ('GABRIEL R.', 'Brasília, DF', '08/02/2026', 'Excelente', 'Capa do Nanami de qualidade. Estampa nítida e material resistente. Vale cada real.', None, 16),
        ('VANESSA L.', 'Belo Horizonte, MG', '31/01/2026', 'Linda', 'Adorei a capa do Nanami. Não descasca e a arte está impecável. Super recomendo.', 'Nanami', 14),
    ]),
    'suguru-geto': ('Suguru Geto', [
        ('THIAGO M.', 'Porto Alegre, RS', '24/02/2026', 'Geto na capa', 'Geto na capa ficou show. Reflexivo lindo, qualidade ótima. Encaixe perfeito no Samsung.', 'Capa Refletiva 3M - Suguru Geto', 17),
        ('FERNANDA N.', 'Campinas, SP', '17/02/2026', 'Presente aprovado', 'Comprei pro meu amigo que curte o Geto. A capa chegou linda, ele adorou. Material bom.', None, 11),
        ('LUCAS W.', 'Recife, PE', '10/02/2026', 'Muito boa', 'Capa do Geto bem feita. A impressão não borra. Recomendo pra fãs de JJK.', None, 13),
        ('MARINA K.', 'Curitiba, PR', '02/02/2026', 'Top', 'A capa do Geto é linda. Material de qualidade. Já quero do Gojo também.', 'Suguru Geto', 15),
    ]),
    # ——— One Piece ———
    'luffy-gear-5': ('Luffy Gear 5', [
        ('GUSTAVO S.', 'São Paulo, SP', '25/02/2026', 'Gear 5 na capa', 'Luffy Gear 5 é lendário. A capa veio incrível, refletivo de qualidade e encaixe perfeito. Chegou rápido.', 'Capa Refletiva 3M - Luffy Gear 5', 35),
        ('AMANDA R.', 'Rio de Janeiro, RJ', '18/02/2026', 'Presente pro meu irmão', 'Ele é viciado em One Piece. A capa do Gear 5 chegou linda, ele ficou maluco. Material bom.', None, 22),
        ('RAFAEL C.', 'Fortaleza, CE', '11/02/2026', 'Melhor capa', 'Capa do Luffy Gear 5 impecável. Estampa nítida, refletivo bonito. Recomendo demais.', None, 28),
        ('JULIANA H.', 'Salvador, BA', '03/02/2026', 'Amei', 'Sou fã do Luffy e essa capa superou. Não descasca e a arte está linda. Já quero do Zoro.', 'Luffy Gear 5', 24),
    ]),
    'zoro': ('Zoro', [
        ('FELIPE M.', 'Curitiba, PR', '23/02/2026', 'Zoro na capa', 'Espadachim favorito. A capa veio linda, refletivo destaca a arte e a qualidade é ótima. Encaixe certo.', 'Capa Refletiva 3M - Zoro', 26),
        ('CAROLINA L.', 'Belo Horizonte, MG', '16/02/2026', 'Pro meu namorado', 'Ele ama o Zoro. A capa chegou perfeita, estampa nítida e material resistente. Ele amou.', None, 15),
        ('MARCOS P.', 'Porto Alegre, RS', '09/02/2026', 'Boa qualidade', 'Capa do Zoro bem feita. A impressão não borra e a capa protege bem. Recomendo.', None, 18),
        ('FERNANDA O.', 'Recife, PE', '01/02/2026', 'Perfeita', 'A capa do Zoro é linda. Material bom e não descasca. Super recomendo.', 'Zoro', 20),
    ]),
    'zoro-ancient': ('Zoro Edição Ancient', [
        ('CAIO P.', 'Campinas, SP', '22/02/2026', 'Zoro Ancient na capa', 'Zoro Ancient é brabo. A capa veio show, refletivo de qualidade e encaixe perfeito no iPhone.', 'Capa Refletiva 3M - Zoro Edição Ancient', 21),
        ('PATRICIA F.', 'Florianópolis, SC', '15/02/2026', 'Presente pro irmão', 'Ele é fã de One Piece e do Zoro. A capa chegou linda, qualidade boa. Aprovado.', None, 13),
        ('BRUNO Q.', 'Vitória, ES', '08/02/2026', 'Excelente', 'Capa do Zoro Ancient de qualidade. Estampa nítida e material resistente. Vale a pena.', None, 16),
        ('ISABELA D.', 'Goiânia, GO', '31/01/2026', 'Linda', 'Adorei a capa do Zoro Ancient. Material de qualidade. Recomendo.', 'Zoro Edição Ancient', 14),
    ]),
    'sanji': ('Sanji', [
        ('LEONARDO R.', 'Santos, SP', '24/02/2026', 'Sanji na capa', 'Cozinheiro do bando na capa ficou show. Reflexivo bonito, qualidade ótima. Encaixou certinho.', 'Capa Refletiva 3M - Sanji', 19),
        ('GABRIELA N.', 'Joinville, SC', '17/02/2026', 'Pro meu filho', 'Ele ama o Sanji. A capa chegou linda, estampa nítida e material bom. Ele adorou.', None, 12),
        ('PEDRO T.', 'Brasília, DF', '10/02/2026', 'Muito boa', 'Capa do Sanji resistente. A arte está perfeita e não descasca. Recomendo.', None, 15),
        ('MARINA U.', 'Manaus, AM', '02/02/2026', 'Amei', 'A capa do Sanji é linda. Material bom e a estampa está impecável. Super recomendo.', 'Sanji', 17),
    ]),
    'ace': ('Ace', [
        ('RODRIGO V.', 'Rio de Janeiro, RJ', '21/02/2026', 'Ace na capa', 'Ace é marcante. A capa veio linda, refletivo de qualidade e encaixe perfeito. Muito satisfeito.', 'Capa Refletiva 3M - Ace', 27),
        ('DANIELA S.', 'São Paulo, SP', '14/02/2026', 'Presente emocionante', 'Comprei pro meu irmão que chora com o Ace. A capa chegou perfeita, ele amou. Material bom.', None, 18),
        ('MARCOS G.', 'Fortaleza, CE', '07/02/2026', 'Qualidade top', 'Capa do Ace impecável. Estampa linda e material resistente. Recomendo pra fãs de OP.', None, 20),
        ('VANESSA M.', 'Salvador, BA', '30/01/2026', 'Perfeita', 'Amei a capa do Ace. Não descasca e a arte está nítida. Vale cada real.', 'Ace', 16),
    ]),
    'shanks': ('Shanks', [
        ('GUSTAVO W.', 'Belo Horizonte, MG', '23/02/2026', 'Shanks na capa', 'Yonkou favorito. A capa veio incrível, refletivo lindo e qualidade ótima. Encaixe certo no Samsung.', 'Capa Refletiva 3M - Shanks', 23),
        ('LETÍCIA T.', 'Curitiba, PR', '16/02/2026', 'Pro meu namorado', 'Ele é fã do Shanks. A capa chegou linda, estampa nítida e material resistente. Aprovado.', None, 14),
        ('FELIPE X.', 'Porto Alegre, RS', '09/02/2026', 'Boa demais', 'Capa do Shanks bem feita. A impressão não borra. Recomendo.', None, 17),
        ('CAMILA Y.', 'Recife, PE', '01/02/2026', 'Top', 'A capa do Shanks é linda. Material de qualidade. Já quero do Luffy também.', 'Shanks', 19),
    ]),
    # ——— Dragon Ball ———
    'goku': ('Goku', [
        ('MARCELO A.', 'São Paulo, SP', '24/02/2026', 'Goku na capa', 'Lendário. A capa do Goku veio linda, refletivo de qualidade e encaixe perfeito. Chegou rápido.', 'Capa Refletiva 3M - Goku', 38),
        ('ADRIANA B.', 'Rio de Janeiro, RJ', '17/02/2026', 'Presente pro meu pai', 'Meu pai é fã de Dragon Ball desde sempre. A capa do Goku chegou linda, ele amou. Material bom.', None, 25),
        ('RAFAEL D.', 'Belo Horizonte, MG', '10/02/2026', 'Nostalgia pura', 'Capa do Goku impecável. Qualidade top, estampa nítida. Recomendo demais pra fãs de DB.', None, 30),
        ('JULIANA E.', 'Curitiba, PR', '02/02/2026', 'Amei', 'Sou fã do Goku e essa capa superou. Não descasca e a arte está linda. Já quero do Vegeta.', 'Goku', 22),
    ]),
    'vegeta': ('Vegeta', [
        ('CAIO F.', 'Campinas, SP', '22/02/2026', 'Vegeta na capa', 'Príncipe dos Sayajins. A capa veio show, refletivo bonito e qualidade ótima. Encaixe certo.', 'Capa Refletiva 3M - Vegeta', 26),
        ('PATRICIA G.', 'Fortaleza, CE', '15/02/2026', 'Pro meu irmão', 'Ele ama o Vegeta. A capa chegou perfeita, estampa nítida e material resistente. Ele adorou.', None, 16),
        ('BRUNO H.', 'Porto Alegre, RS', '08/02/2026', 'Excelente', 'Capa do Vegeta de qualidade. A arte está perfeita e não descasca. Recomendo.', None, 19),
        ('ISABELA I.', 'Salvador, BA', '31/01/2026', 'Linda', 'Adorei a capa do Vegeta. Material bom e a estampa está impecável. Super recomendo.', 'Vegeta', 18),
    ]),
    'freeza': ('Freeza', [
        ('LEONARDO J.', 'Brasília, DF', '21/02/2026', 'Freeza na capa', 'Vilão clássico. A capa veio linda, refletivo de qualidade e encaixe perfeito no celular.', 'Capa Refletiva 3M - Freeza', 20),
        ('GABRIELA K.', 'Florianópolis, SC', '14/02/2026', 'Presente aprovado', 'Comprei pro meu amigo que é fã do Freeza. A capa chegou linda, ele amou. Material resistente.', None, 12),
        ('PEDRO L.', 'Recife, PE', '07/02/2026', 'Muito boa', 'Capa do Freeza bem feita. Estampa nítida e não descasca. Recomendo pra fãs de Dragon Ball.', None, 15),
        ('MARINA M.', 'Manaus, AM', '30/01/2026', 'Perfeita', 'A capa do Freeza é linda. Material de qualidade. Vale a pena.', 'Freeza', 14),
    ]),
}

def build_reviews_list(slug):
    if slug not in REVIEWS:
        return None
    display_name, reviews = REVIEWS[slug]
    parts = []
    for r in reviews:
        parts.append(article(r[0], r[1], r[2], r[3], r[4], r[5] if len(r) > 5 else None, r[6] if len(r) > 6 else 12))
    return '\n'.join(parts)

def main():
    for slug, (display_name, _) in REVIEWS.items():
        path = os.path.join(PRODUTO_DIR, f'capa-reflexiva-3m-{slug}.html')
        if not os.path.isfile(path):
            print(f'AVISO: {path} não encontrado')
            continue
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        new_list = build_reviews_list(slug)
        if not new_list:
            continue
        # Padrão: desde <div class="pdp__reviews-list"> até o </div> que fecha a lista (antes de </section>)
        pattern = r'(<div class="pdp__reviews-list">)\n(.*)\n(      </div>\n    </section>)'
        match = re.search(pattern, content, re.DOTALL)
        if not match:
            print(f'AVISO: bloco de reviews não encontrado em {path}')
            continue
        new_block = match.group(1) + '\n' + new_list + '\n' + match.group(3)
        content_new = content[:match.start()] + new_block + content[match.end():]
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content_new)
        print(f'OK: {path}')
    print('Concluído.')

if __name__ == '__main__':
    main()
