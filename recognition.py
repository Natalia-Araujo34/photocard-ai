# pip install torch torchvision transformers faiss-cpu pillow matplotlib

import os
import torch
import faiss
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import matplotlib.pyplot as plt
import shutil  # pra copiar arquivos
import json   # para metadados

# 1. Carregar modelo CLIP
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# 2. Função para gerar embedding de uma imagem
def get_embedding(image_path):
    image = Image.open(image_path).convert("RGB")
    inputs = processor(images=image, return_tensors="pt", padding=True)
    with torch.no_grad():
        emb = model.get_image_features(**inputs)
    return emb[0].cpu().numpy()

# 3. Função para criar banco e índice FAISS
def build_index():
    reference_embeddings = []
    labels = []
    file_paths = []

    for person in ["jongho", "hongjoong", "seonghwa"]:
        folder = f"data/{person}"
        if not os.path.exists(folder):
            continue
        for img_name in os.listdir(folder):
            img_path = os.path.join(folder, img_name)
            emb = get_embedding(img_path)
            reference_embeddings.append(emb)
            labels.append(person)
            file_paths.append(img_path)

    if len(reference_embeddings) == 0:
        return None, None, None

    reference_embeddings = torch.tensor(reference_embeddings).numpy()
    d = reference_embeddings.shape[1]
    index = faiss.IndexFlatL2(d)
    index.add(reference_embeddings)
    return index, labels, file_paths

# Cria índice inicial
index, labels, file_paths = build_index()

# 4. Função para identificar e mostrar resultados
def identify_and_show(image_path, top_k=3):
    query_emb = get_embedding(image_path).reshape(1, -1)
    distances, indices = index.search(query_emb, top_k)
    
    results = [(labels[i], file_paths[i], float(distances[0][j])) for j, i in enumerate(indices[0])]
    
    fig, axes = plt.subplots(1, top_k + 1, figsize=(15,5))
    
    # Foto nova
    new_img = Image.open(image_path)
    axes[0].imshow(new_img)
    axes[0].set_title("Foto Nova")
    axes[0].axis('off')
    
    # Top_k fotos do banco
    for j, (label, path, dist) in enumerate(results):
        img = Image.open(path)
        axes[j+1].imshow(img)
        axes[j+1].set_title(f"{label}\nDist={dist:.2f}")
        axes[j+1].axis('off')
    
    plt.show()
    return results

# 5. Função para adicionar metadados no JSON
def add_metadata(filename, member, album="Unknown", version="Unknown", rarity="Unknown", price=0):
    metadata_file = "cards.json"
    if os.path.exists(metadata_file):
        with open(metadata_file, "r") as f:
            data = json.load(f)
    else:
        data = []

    if not any(d["filename"] == filename for d in data):
        data.append({
            "filename": filename,
            "member": member,
            "album": album,
            "version": version,
            "rarity": rarity,
            "price": price
        })

    with open(metadata_file, "w") as f:
        json.dump(data, f, indent=4)

# 6. Função CORRIGIDA para identificar e salvar com threshold
def identify_and_save_with_metadata(image_path, top_k=3, auto_add=True,
                                    album="Unknown", version="Unknown",
                                    rarity="Unknown", price=0, distance_threshold=30):
    global index, labels, file_paths

    resultados = identify_and_show(image_path, top_k)
    top_label, _, dist = resultados[0]
    print(f"Top candidato: {top_label}, distância: {dist:.4f}")

    if not auto_add:
        return resultados

    new_file_name = os.path.basename(image_path)

    if dist > distance_threshold:
        # Se a distância for grande demais, classifica como "unsorted"
        unsorted_folder = os.path.join("data", "unsorted")
        os.makedirs(unsorted_folder, exist_ok=True)
        destino = os.path.join(unsorted_folder, new_file_name)
        shutil.copy(image_path, destino)
        print(f"⚠️ Distância alta ({dist:.2f}). Foto movida para: {destino}")
        add_metadata(new_file_name, "unsorted", album, version, rarity, price)
        print("⚠️ Metadados salvos com member='unsorted'")
        return resultados

    # Caso contrário, adiciona normalmente
    member_folder = os.path.join("data", top_label)
    os.makedirs(member_folder, exist_ok=True)
    destino = os.path.join(member_folder, new_file_name)
    shutil.copy(image_path, destino)
    print(f"✅ Foto adicionada ao banco de {top_label}: {destino}")

    # Atualiza índice FAISS
    emb = get_embedding(destino).reshape(1, -1)
    index.add(emb)
    labels.append(top_label)
    file_paths.append(destino)
    print("✅ Índice FAISS atualizado com a nova foto.")

    add_metadata(new_file_name, top_label, album, version, rarity, price)
    print("✅ Metadados salvos no cards.json")

    return resultados

# ----------------
# Teste após a função corrigida
# ----------------
test_img = "test/test.jpg"
resultados = identify_and_save_with_metadata(test_img, distance_threshold=30)
print("Top 3 candidatos:", resultados)
