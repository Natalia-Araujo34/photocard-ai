import json
import os
from PIL import Image
import matplotlib.pyplot as plt

def show_binder(json_file="cards.json", data_folder="data", member_filter=None, rarity_filter=None, version_filter=None):
    if not os.path.exists(json_file):
        print("❌ cards.json não encontrado!")
        return

    with open(json_file, "r") as f:
        cards = json.load(f)

    # Aplicar filtros
    filtered_cards = []
    for card in cards:
        if member_filter and card.get("member") != member_filter:
            continue
        if rarity_filter and card.get("rarity") != rarity_filter:
            continue
        if version_filter and card.get("version") != version_filter:
            continue
        filtered_cards.append(card)

    if not filtered_cards:
        print("📂 Nenhum card encontrado com os filtros aplicados!")
        return

    n_cards = len(filtered_cards)
    cols = 5
    rows = (n_cards + cols - 1) // cols

    fig, axes = plt.subplots(rows, cols, figsize=(cols*3, rows*3))
    axes = axes.flatten()

    for i, card in enumerate(filtered_cards):
        member = card.get("member", "Unknown")
        filename = card.get("filename", "")
        album = card.get("album", "Unknown")
        version = card.get("version", "Unknown")
        rarity = card.get("rarity", "Unknown")
        price = card.get("price", "Unknown")

        img_path = os.path.join(data_folder, member, filename)
        if os.path.exists(img_path):
            img = Image.open(img_path)
            axes[i].imshow(img)
        else:
            axes[i].text(0.5, 0.5, "Imagem não encontrada", ha='center', va='center')
            axes[i].set_facecolor('lightgray')

        axes[i].set_title(f"{member}\n{album}, {version}\n{rarity}, ${price}")
        axes[i].axis('off')

    # Oculta eixos extras
    for j in range(i+1, len(axes)):
        axes[j].axis('off')

    plt.tight_layout()
    plt.show()

# Exemplo de uso interativo:
# Mostrar todos os cards
#show_binder()

# Mostrar só os cards do Seonghwa
show_binder(member_filter="seonghwa")

# Mostrar só cards raros
# show_binder(rarity_filter="Rare")
