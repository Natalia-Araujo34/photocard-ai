# edit_cards_web_v2.py
import streamlit as st
from PIL import Image
import os
import json

# Caminhos
DATA_FOLDER = "data"
METADATA_FILE = "cards.json"
UNSORTED_FOLDER = os.path.join(DATA_FOLDER, "unsorted")
os.makedirs(UNSORTED_FOLDER, exist_ok=True)

# --- Funções ---
def load_metadata():
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_metadata(data):
    with open(METADATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_card_path(card):
    member = card["member"]
    filename = card["filename"]
    path = os.path.join(DATA_FOLDER, member, filename) if member != "unsorted" else os.path.join(UNSORTED_FOLDER, filename)
    return path if os.path.exists(path) else None

# --- Interface ---
st.title("Photocard Collection Manager")

metadata = load_metadata()

# Filtro por membro
members = ["todos"] + list({card["member"] for card in metadata})
selected_member = st.selectbox("Filtrar por membro:", members)

st.header("Minha Coleção")
for i, card in enumerate(metadata):
    if selected_member != "todos" and card["member"] != selected_member:
        continue
    path = get_card_path(card)
    if path:
        cols = st.columns([1, 2, 2])
        with cols[0]:
            # Thumbnail menor
            img = Image.open(path)
            img.thumbnail((150, 150))
            st.image(img, use_container_width=True)

        with cols[1]:
            st.text(f"Membro: {card['member']}")
            st.text(f"Album: {card['album']}")
            st.text(f"Versão: {card['version']}")
            st.text(f"Raridade: {card['rarity']}")
            st.text(f"Preço: {card['price']}")

        with cols[2]:
            # Permitir edição de metadados
            with st.expander("Editar metadados"):
                new_member = st.text_input("Membro", value=card['member'], key=f"member_{i}")
                new_album = st.text_input("Album", value=card['album'], key=f"album_{i}")
                new_version = st.text_input("Versão", value=card['version'], key=f"version_{i}")
                new_rarity = st.text_input("Raridade", value=card['rarity'], key=f"rarity_{i}")
                new_price = st.number_input("Preço", value=float(card['price']), step=0.01, key=f"price_{i}")

                if st.button("Salvar alterações", key=f"save_{i}"):
                    card['member'] = new_member
                    card['album'] = new_album
                    card['version'] = new_version
                    card['rarity'] = new_rarity
                    card['price'] = new_price
                    save_metadata(metadata)
                    st.success("Metadados atualizados!")
