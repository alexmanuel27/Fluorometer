import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
import os
import re

# ==========================================
# 1. CONFIGURACIÓN
# ==========================================
RUTA = 'D:/PhD/Investigacion/Belgium(2026-2027)/newFluorometer/completo/10_11_2026(kaolin-extracto)/90°'

SATURACION = 4294967296.0  # Valor de saturación del sensor

grupos = {
    'Blanco (Etanol)':    r'blanco_etanol\d+',
    'Extracto Puro':      r'extracto_puro\d+',
    'Extracto+Kaolín A':  r'extracto\+kaolin_a\d+',
    'Extracto+Kaolín B':  r'extracto\+kaolin_b\d+',
    'Kaolín A solo':      r'kaolin_a\d+',
    'Kaolín B solo':      r'kaolin_b\d+',
}

wl_clave = [435, 680, 730]
colors_grupos = {
    'Blanco (Etanol)':    '#999999',
    'Extracto Puro':      '#1f77b4',
    'Extracto+Kaolín A':  '#ff7f0e',
    'Extracto+Kaolín B':  '#2ca02c',
    'Kaolín A solo':      '#d62728',
    'Kaolín B solo':      '#9467bd',
}

# ==========================================
# 2. LECTURA Y AGRUPACIÓN DE DATOS (CON FILTRO DE SATURACIÓN)
# ==========================================
todos_csv = sorted(glob.glob(os.path.join(RUTA, '*.csv')))
print(f"📁 Total de archivos CSV: {len(todos_csv)}")
print("\n📄 Archivos encontrados:")
for f in todos_csv:
    print(f"   - {os.path.basename(f)}")

datos_grupos = {g: [] for g in grupos.keys()}
archivos_sin_grupo = []

for archivo in todos_csv:
    nombre = os.path.basename(archivo).replace('.csv', '').replace('.CSV', '')
    df = pd.read_csv(archivo)
    
    # Normalizar nombres de columnas
    df.columns = [c.strip().lower() for c in df.columns]
    
    # Identificar columnas
    if any('wavel' in c for c in df.columns):
        wl_col = [c for c in df.columns if 'wavel' in c][0]
        int_col = [c for c in df.columns if 'mean_inten' in c][0]
    else:
        wl_col = df.columns[0]
        int_col = df.columns[1]
    
    # Convertir a numérico y filtrar filas no numéricas
    df[wl_col] = pd.to_numeric(df[wl_col], errors='coerce')
    df = df.dropna(subset=[wl_col])
    
    # FILTRO CRÍTICO: Reemplazar valores de saturación con NaN
    df[int_col] = pd.to_numeric(df[int_col], errors='coerce')
    df[int_col] = df[int_col].replace(SATURACION, np.nan)
    df[int_col] = df[int_col].replace(0.0, np.nan)
    
    serie = df.set_index(wl_col)[int_col]
    serie.index = serie.index.astype(float)
    
    # Asignar a grupo
    asignado = False
    for grupo, patron in grupos.items():
        if re.match(patron, nombre, re.IGNORECASE):
            datos_grupos[grupo].append(serie)
            asignado = True
            break
    
    if not asignado:
        archivos_sin_grupo.append(nombre)

# Diagnóstico
print("\n" + "="*60)
print("DIAGNÓSTICO DE AGRUPACIÓN")
print("="*60)
for g, lista in datos_grupos.items():
    print(f"   {g}: {len(lista)} replicados")

if archivos_sin_grupo:
    print(f"\n⚠️  Archivos no asignados a ningún grupo:")
    for n in archivos_sin_grupo:
        print(f"   - {n}")

# ==========================================
# 3. CÁLCULO DE MEDIAS Y STD POR GRUPO
# ==========================================
medias = {}
stds = {}
for g, lista in datos_grupos.items():
    if len(lista) > 0:
        df_rep = pd.DataFrame(lista)
        medias[g] = df_rep.mean()
        stds[g] = df_rep.std()
        print(f"✅ {g}: media max = {medias[g].max():.2f}, media min = {medias[g].min():.2f}")

wl_all = sorted(medias[list(medias.keys())[0]].index.tolist())

# ==========================================
# 4. ANÁLISIS DE ATENUACIÓN DEL KAOLÍN
# ==========================================
print("\n" + "="*60)
print("ANÁLISIS DE ATENUACIÓN POR KAOLÍN")
print("="*60)

if 'Extracto Puro' in medias and 'Extracto+Kaolín A' in medias:
    for wl in wl_clave:
        val_puro = medias['Extracto Puro'].get(wl, np.nan)
        val_ka = medias['Extracto+Kaolín A'].get(wl, np.nan)
        val_kb = medias['Extracto+Kaolín B'].get(wl, np.nan)
        
        if not np.isnan(val_puro) and val_puro != 0:
            red_a = (1 - val_ka / val_puro) * 100
            red_b = (1 - val_kb / val_puro) * 100
            print(f"λ = {wl} nm | Atenuación Kaolín A: {red_a:.1f}% | Kaolín B: {red_b:.1f}%")
        else:
            print(f"λ = {wl} nm | Señal de extracto puro demasiado baja para calcular atenuación")

# ==========================================
# 5. FIGURA 1: ESPECTROS COMPLETOS POR GRUPO (CON ESCALA LOG)
# ==========================================
fig1, ax1 = plt.subplots(figsize=(12, 7))

for g in grupos.keys():
    if g in medias:
        ax1.plot(medias[g].index, medias[g].values, 
                 color=colors_grupos[g], linewidth=2, label=g)
        ax1.fill_between(medias[g].index, 
                         medias[g].values - stds[g].values,
                         medias[g].values + stds[g].values,
                         color=colors_grupos[g], alpha=0.15)

ax1.set_xlabel('Longitud de onda (nm)', fontsize=12)
ax1.set_ylabel('Intensidad media (i.u.)', fontsize=12)
ax1.set_title('Espectros de fluorescencia por condición experimental', fontsize=14, fontweight='bold')
ax1.legend(loc='best', fontsize=10, framealpha=0.9)
ax1.grid(True, linestyle=':', alpha=0.5)
ax1.set_xlim(400, 950)
ax1.set_yscale('log')  # ESCALA LOGARÍTMICA para ver todas las curvas

plt.tight_layout()
plt.savefig('Fig1_Espectros_por_grupo.png', dpi=300, bbox_inches='tight')
print("\n✅ Figura 1 guardada")
plt.show()

# ==========================================
# 6. FIGURA 2: ESPECTROS CORREGIDOS (Blanco restado)
# ==========================================
blanco = medias['Blanco (Etanol)']

fig2, ax2 = plt.subplots(figsize=(12, 7))

for g in grupos.keys():
    if g != 'Blanco (Etanol)' and g in medias:
        señal = medias[g] - blanco
        error = np.sqrt(stds[g]**2 + stds['Blanco (Etanol)']**2)
        
        ax2.plot(señal.index, señal.values, 
                 color=colors_grupos[g], linewidth=2, label=g)
        ax2.fill_between(señal.index, 
                         señal.values - error.values,
                         señal.values + error.values,
                         color=colors_grupos[g], alpha=0.15)

ax2.axhline(y=0, color='black', linestyle='--', linewidth=0.8, alpha=0.5)
ax2.set_xlabel('Longitud de onda (nm)', fontsize=12)
ax2.set_ylabel('Intensidad neta (Muestra − Blanco)', fontsize=12)
ax2.set_title('Espectros corregidos (señal neta tras restar blanco de etanol)', fontsize=14, fontweight='bold')
ax2.legend(loc='best', fontsize=10, framealpha=0.9)
ax2.grid(True, linestyle=':', alpha=0.5)
ax2.set_xlim(400, 950)

plt.tight_layout()
plt.savefig('Fig2_Espectros_corregidos.png', dpi=300, bbox_inches='tight')
print("✅ Figura 2 guardada")
plt.show()

# ==========================================
# 7. FIGURA 3: COMPARACIÓN EN λ CLAVE (Barras con error + % atenuación)
# ==========================================
fig3, axes3 = plt.subplots(1, len(wl_clave), figsize=(15, 6), sharey=False)

for ax, wl in zip(axes3, wl_clave):
    grupos_plot = [g for g in grupos.keys() if g != 'Blanco (Etanol)']
    x_pos = np.arange(len(grupos_plot))
    
    valores = []
    errores = []
    for g in grupos_plot:
        val = medias[g].get(wl, np.nan) - blanco.get(wl, np.nan)
        err = np.sqrt(stds[g].get(wl, 0)**2 + stds['Blanco (Etanol)'].get(wl, 0)**2)
        valores.append(val)
        errores.append(err)
    
    barras = ax.bar(x_pos, valores, yerr=errores, capsize=5,
                    color=[colors_grupos[g] for g in grupos_plot], 
                    edgecolor='black', linewidth=0.5, alpha=0.85)
    
    # Añadir texto con % de atenuación sobre las barras de kaolín
    val_puro = medias['Extracto Puro'].get(wl, np.nan) - blanco.get(wl, np.nan)
    for i, g in enumerate(grupos_plot):
        if 'Kaolín' in g and 'Extracto' in g:
            val_g = medias[g].get(wl, np.nan) - blanco.get(wl, np.nan)
            if not np.isnan(val_puro) and val_puro != 0:
                pct = (1 - val_g / val_puro) * 100
                ax.text(i, valores[i] + errores[i] + 0.5, f'-{pct:.0f}%', 
                        ha='center', va='bottom', fontsize=9, fontweight='bold', color='red')
    
    ax.set_title(f'λ = {wl} nm', fontsize=13, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels([g.replace('Extracto+', 'Ext+').replace(' solo', '') 
                        for g in grupos_plot], rotation=35, ha='right', fontsize=9)
    ax.set_ylabel('Intensidad neta (i.u.)', fontsize=11)
    ax.grid(axis='y', linestyle=':', alpha=0.5)
    ax.axhline(y=0, color='black', linewidth=0.8, alpha=0.4)

fig3.suptitle('Intensidad neta en longitudes de onda clave\n(Muestra − Blanco de etanol)', 
              fontsize=14, fontweight='bold', y=1.02)

plt.tight_layout()
plt.savefig('Fig3_Comparacion_lambda_clave.png', dpi=300, bbox_inches='tight')
print("✅ Figura 3 guardada")
plt.show()

# ==========================================
# 8. FIGURA 4: HEATMAP ESPECTRAL
# ==========================================
grupos_heatmap = [g for g in grupos.keys() if g != 'Blanco (Etanol)']
wl_rango = [wl for wl in wl_all if 400 <= wl <= 800]

matriz = np.zeros((len(grupos_heatmap), len(wl_rango)))
for i, g in enumerate(grupos_heatmap):
    for j, wl in enumerate(wl_rango):
        val = medias[g].get(wl, np.nan) - blanco.get(wl, np.nan)
        matriz[i, j] = val if not np.isnan(val) else 0

fig4, ax4 = plt.subplots(figsize=(12, 6))
im = ax4.imshow(matriz, aspect='auto', cmap='viridis', interpolation='nearest')

ax4.set_yticks(np.arange(len(grupos_heatmap)))
ax4.set_yticklabels(grupos_heatmap, fontsize=10)
ax4.set_xticks(np.arange(0, len(wl_rango), 5))
ax4.set_xticklabels([f'{int(wl_rango[i])}' for i in np.arange(0, len(wl_rango), 5)], 
                    rotation=45, ha='right', fontsize=9)
ax4.set_xlabel('Longitud de onda (nm)', fontsize=12)
ax4.set_title('Heatmap: Intensidad neta (Muestra − Blanco)', fontsize=14, fontweight='bold')

cbar = plt.colorbar(im, ax=ax4)
cbar.set_label('Intensidad neta (i.u.)', fontsize=11)

plt.tight_layout()
plt.savefig('Fig4_Heatmap_espectral.png', dpi=300, bbox_inches='tight')
print("✅ Figura 4 guardada")
plt.show()

# ==========================================
# 9. FIGURA 5: GRÁFICO DE ATENUACIÓN (%) vs λ
# ==========================================
fig5, ax5 = plt.subplots(figsize=(10, 6))

wl_aten = [wl for wl in wl_all if 400 <= wl <= 800]
pct_a = []
pct_b = []
for wl in wl_aten:
    vp = medias['Extracto Puro'].get(wl, np.nan) - blanco.get(wl, np.nan)
    va = medias['Extracto+Kaolín A'].get(wl, np.nan) - blanco.get(wl, np.nan)
    vb = medias['Extracto+Kaolín B'].get(wl, np.nan) - blanco.get(wl, np.nan)
    
    if not np.isnan(vp) and vp != 0:
        pct_a.append((1 - va / vp) * 100)
        pct_b.append((1 - vb / vp) * 100)
    else:
        pct_a.append(np.nan)
        pct_b.append(np.nan)

ax5.plot(wl_aten, pct_a, 'o-', color='#ff7f0e', linewidth=1.5, markersize=5, label='Kaolín A')
ax5.plot(wl_aten, pct_b, 's-', color='#2ca02c', linewidth=1.5, markersize=5, label='Kaolín B')
ax5.axhline(y=0, color='black', linestyle='--', linewidth=0.8, alpha=0.5)
ax5.set_xlabel('Longitud de onda (nm)', fontsize=12)
ax5.set_ylabel('Atenuación (%)', fontsize=12)
ax5.set_title('Efecto de atenuación del kaolín sobre la señal del extracto\n(% de reducción respecto al extracto puro)', 
              fontsize=14, fontweight='bold')
ax5.legend(loc='best', fontsize=11)
ax5.grid(True, linestyle=':', alpha=0.5)

plt.tight_layout()
plt.savefig('Fig5_Atenuacion_kaolin_vs_lambda.png', dpi=300, bbox_inches='tight')
print("✅ Figura 5 guardada: Atenuación % vs λ")
plt.show()

print("\n🎉 Todas las figuras generadas exitosamente.")