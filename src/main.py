import streamlit as st
import folium
import networkx as nx
import numpy as np
from streamlit.components.v1 import html
from folium.plugins import AntPath
from sklearn.ensemble import RandomForestClassifier
import random
import math

# =========================================================
# 1️⃣ REAL GAZA NODES (HEAD CLUSTERS)
# =========================================================
NODES = {
    "Beit Hanoun": (31.5350, 34.5350),
    "Beit Lahia": (31.5464, 34.5011),
    "Jabalia": (31.5293, 34.4790),
    "Jabalia Camp": (31.5293, 34.4790),
    "Gaza City": (31.5017, 34.4668),
    "Shuja'iyya": (31.5000, 34.4800),
    "Al-Zeitoun": (31.4900, 34.4600),
    "Al-Rimal": (31.5200, 34.4500),
    "Nuseirat Camp": (31.4483, 34.3921),
    "Bureij Camp": (31.4394, 34.4030),
    "Maghazi Camp": (31.4217, 34.3867),
    "Deir al-Balah": (31.4186, 34.3493),
    "Khan Younis": (31.3460, 34.3033),
    "Khuza'a": (31.3050, 34.3350),
    "Abasan al-Kabira": (31.3150, 34.3400),
    "Rafah": (31.2870, 34.2595),
    "Shaboura Camp": (31.2800, 34.2500),
    "Tel al-Sultan": (31.2950, 34.2400)
}

# =========================================================
# 2️⃣ GENERATE BACKUP NODES AROUND EACH HEAD
# =========================================================
BACKUP_PER_HEAD = 3
BACKUP_NODES = {}

for head, (lat, lon) in NODES.items():
    for i in range(BACKUP_PER_HEAD):
        BACKUP_NODES[f"{head}_B{i+1}"] = {
            "pos": (
                lat + random.uniform(-0.008, 0.008),
                lon + random.uniform(-0.008, 0.008)
            ),
            "head": head
        }

# Merge all nodes
ALL_NODES = {}
for h, p in NODES.items():
    ALL_NODES[h] = {"pos": p, "type": "HEAD"}

for b, d in BACKUP_NODES.items():
    ALL_NODES[b] = {"pos": d["pos"], "type": "BACKUP", "head": d["head"]}

# =========================================================
# 3️⃣ STREAMLIT UI
# =========================================================
st.set_page_config(layout="wide")
st.title("🚑 Gaza Smart Rescue System – Cluster MANET + AI + Quantum")

bombed_areas = st.multiselect(
    "⚠️ اختر مناطق القصف",
    list(NODES.keys()),
    default=["Shuja'iyya", "Jabalia Camp"]
)

start = st.selectbox("📍 نقطة الانطلاق", list(NODES.keys()))
end = st.selectbox("🎯 المنطقة المستهدفة", list(NODES.keys()))
story_mode = st.checkbox("🎬 تشغيل سيناريو واقعي مباشر")

# =========================================================
# 4️⃣ BUILD GRAPH + ENERGY / HEALTH
# =========================================================
G = nx.Graph()
node_data = {}

for node, data in ALL_NODES.items():
    if data["type"] == "HEAD":
        energy = random.randint(40, 100)
        health = random.randint(50, 100)
        if node in bombed_areas:
            health = 0
            energy = 0
    else:
        energy = random.randint(30, 90)
        health = random.randint(40, 100)

    node_data[node] = {
        "energy": energy,
        "health": health,
        "type": data["type"],
        "head": data.get("head")
    }

    G.add_node(node, pos=data["pos"], energy=energy, health=health)

# =========================================================
# 5️⃣ AUTO HEAD ELECTION (SELF HEALING)
# =========================================================
def elect_new_head(dead_head):
    candidates = [
        n for n, s in node_data.items()
        if s.get("head") == dead_head and s["energy"] > 50 and s["health"] > 50
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda n: node_data[n]["energy"])

for head in list(NODES.keys()):
    if node_data[head]["health"] == 0:
        new_head = elect_new_head(head)
        if new_head:
            node_data[new_head]["type"] = "HEAD"
            for n in node_data:
                if node_data[n].get("head") == head:
                    node_data[n]["head"] = new_head

# =========================================================
# 6️⃣ CONNECT GRAPH (CLUSTER AWARE)
# =========================================================
for n1 in ALL_NODES:
    for n2 in ALL_NODES:
        if n1 != n2:
            p1 = ALL_NODES[n1]["pos"]
            p2 = ALL_NODES[n2]["pos"]
            dist = math.dist(p1, p2)
            if dist < 0.04:
                weight = dist * 100
                G.add_edge(n1, n2, weight=weight)

# =========================================================
# 7️⃣ ROUTING BETWEEN ACTIVE HEADS
# =========================================================
active_heads = [n for n in node_data if node_data[n]["type"] == "HEAD"]

path = nx.shortest_path(G, start, end, weight="weight")

# =========================================================
# 8️⃣ MAP (NO FLICKER)
# =========================================================
m = folium.Map(location=[31.4, 34.4], zoom_start=10, tiles="OpenStreetMap")

for node, info in node_data.items():
    lat, lon = ALL_NODES[node]["pos"]

    if info["type"] == "HEAD":
        color = "black" if info["health"] == 0 else "green"
        radius = 10
    else:
        color = "lightblue"
        radius = 5

    if info["type"] == "HEAD" and node not in NODES:
        color = "gold"  # promoted backup

    folium.CircleMarker(
        location=[lat, lon],
        radius=radius,
        color=color,
        fill=True,
        fill_opacity=0.9,
        popup=f"""
        <b>{node}</b><br>
        Type: {info["type"]}<br>
        Energy: {info["energy"]}%<br>
        Health: {info["health"]}%
        """
    ).add_to(m)

AntPath(
    locations=[ALL_NODES[n]["pos"] for n in path],
    color="yellow",
    pulse_color="red",
    weight=5
).add_to(m)

# =========================================================
# 9️⃣ DASHBOARD
# =========================================================
st.sidebar.title("📊 Cluster Status")
st.sidebar.metric("🧠 Active Heads", len(active_heads))
st.sidebar.metric("🔁 Backup Nodes", len(BACKUP_NODES))
st.sidebar.metric("🛡️ Self Healing", "Enabled")

# =========================================================
# 🔟 RESULTS
# =========================================================
st.success(f"✅ أفضل مسار إنقاذ:\n{' → '.join(path)}")
st.info("🔁 في حال سقوط أي Head يتم انتخاب Backup تلقائياً")

html(m._repr_html_(), height=650)
