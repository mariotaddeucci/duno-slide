# 🎨 duno-slide

> **Gerador de slides minimalista e elegante inspirado nas lives de Python do [Eduardo Mendes (dunossauro)](https://github.com/dunossauro)** ✨

## 📖 Sobre

**duno-slide** é uma biblioteca Python para criar apresentações profissionais a partir de um arquivo TOML. Simples, direto e sem complicações.

## ✨ Principais características

- 🎯 **Simples**: Configure seus slides em um arquivo TOML
- 🎨 **6 cores**: Paleta profissional e elegante
- 📊 **Mermaid**: Diagramas integrados
- 💻 **Syntax highlighting**: GitHub Dark theme automático
- 📐 **Sistema de Grid**: Organize conteúdo em layouts flexíveis
- ⚡ **CLI moderna**: Com Typer
- 📱 **Responsivo**: 16:9 e 4:3

## 🚀 Início rápido

```bash
# Apresentação de exemplo
uvx --from 'duno-slide @ git+https://github.com/mariotaddeucci/duno-slide' duno-slide sample
```

Acesse: http://localhost:8765

## 🚀 Instalação

### Via uvx (recomendado - sem instalar)

```bash
uvx --from 'duno-slide @ git+https://github.com/mariotaddeucci/duno-slide' duno-slide [comando]
```

### Via pip (direto do GitHub)

```bash
pip install 'duno-slide @ git+https://github.com/mariotaddeucci/duno-slide'
```

### Com suporte a exportação (PDF/PNG)

```bash
pip install 'duno-slide[export] @ git+https://github.com/mariotaddeucci/duno-slide'
playwright install chromium
```

## 💻 CLI - Interface de linha de comando

```bash
# Apresentação de exemplo (veja todos os recursos)
duno-slide sample

# Servir sua apresentação
duno-slide host minha_apresentacao.toml

# Renderizar para HTML
duno-slide render minha_apresentacao.toml -o output.html

# Exportar para PDF/PNG
duno-slide export minha_apresentacao.toml -o presentation.pdf -f pdf
```

> **Dica:** Execute `duno-slide sample` e abra http://localhost:8765 para ver todos os recursos, layouts e opções disponíveis, incluindo exemplos de Markdown, Mermaid, tabelas e syntax highlighting.

## 🎨 Cores disponíveis

| Cor | Nome |
|-----|------|
| 🔴 | `red` |
| 🟢 | `green` |
| 🟡 | `yellow` |
| 🔵 | `blue` |
| 🟣 | `lavender` |
| 🌸 | `pink` |

## 📐 Tipos de Slides

### `cover_title_right`
Capa com título grande à direita.

```toml
[[slides]]
layout = "cover_title_right"
background = "red"
title = "Título"
subtitle = "Subtítulo"
```

### `cover_title_left`
Capa com título grande à esquerda.

```toml
[[slides]]
layout = "cover_title_left"
background = "blue"
title = "Título"
```

### `default`
Slide versátil com Markdown, código, tabelas, imagens.

```toml
[[slides]]
layout = "default"
background = "green"
title = "Conteúdo"
content = """
## Seção
- Item 1
- Item 2

[código, tabelas, imagens, etc]
"""
footer = "Rodapé"
```

### `summary`
Sumário em duas colunas.

```toml
[[slides]]
layout = "summary"
background = "yellow"
title = "Agenda"

[[slides.items]]
title = "Tópico 1"
description = "Descrição"

[[slides.items]]
title = "Tópico 2"
```

---

## 📐 Sistema de Grid

Organize conteúdo em layouts de grid flexíveis (semelhante ao Material MkDocs):

### Grid de 2 colunas (padrão)

```toml
[[slides]]
layout = "default"
background = "blue"
title = "Grid Exemplo"
content = """
::: grid
::: card
### Coluna 1
- Item A
- Item B
:::
::: card
### Coluna 2
- Item X
- Item Y
:::
:::
"""
```

### Grid de 3 ou 4 colunas

```toml
content = """
::: grid cols-3
::: card
**Recurso 1**
Descrição
:::
::: card
**Recurso 2**
Descrição
:::
::: card
**Recurso 3**
Descrição
:::
:::
"""
```

Suporta `cols-1`, `cols-2`, `cols-3` e `cols-4`. Cada card pode conter qualquer conteúdo Markdown: títulos, listas, código, etc.

---

## 📝 Exemplo Completo

Para ver um exemplo completo de todas as funcionalidades (Markdown, Mermaid, tabelas, código, etc):

```bash
duno-slide sample
```

Acesse http://localhost:8765 e explore todos os recursos.

---

## 🙏 Agradecimentos

Homenagem ao trabalho do [Eduardo Mendes (dunossauro)](https://github.com/dunossauro) e suas lives de Python.

## 📜 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

---

**Feito com ❤️ inspirado nas lives de Python do dunossauro**

