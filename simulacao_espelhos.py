import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, TextBox, CheckButtons
from matplotlib.patches import FancyArrowPatch

# Configuração inicial
fig, ax = plt.subplots(figsize=(12, 12))
plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.3)

# Parâmetros iniciais
theta_deg = 60  # ângulo entre espelhos em graus
obj_radius = 3.0  # distância do objeto à origem
obj_angle_deg = 30  # ângulo do objeto em graus
show_rays = False  # mostrar raios de luz

# Limites do gráfico
ax.set_xlim(-5, 5)
ax.set_ylim(-5, 5)
ax.set_aspect('equal')
ax.grid(True, alpha=0.3)
ax.set_title('Simulação de Espelhos Angulares - Óptica Geométrica')
ax.set_xlabel('X')
ax.set_ylabel('Y')

# Desenhar origem
ax.plot(0, 0, 'ko', markersize=8, zorder=10)

# Variáveis para armazenar elementos gráficos
mirror_lines = []
obj_point = None
image_points = []
image_annotations = []  # PARA ARMAZENAR AS ANOTAÇÕES DOS NÚMEROS
text_info = None
ray_lines = []
formula_text = None
annotation_text = None

def calculate_images():
    """Calcula todas as imagens usando reflexões sucessivas"""
    # Converter para radianos
    theta = np.radians(theta_deg)
    obj_angle = np.radians(obj_angle_deg)
    
    # Coordenadas do objeto
    obj_x = obj_radius * np.cos(obj_angle)
    obj_y = obj_radius * np.sin(obj_angle)
    
    # Calcular número teórico de imagens
    n = theta_deg
    if n == 0:
        return [], [], 0, "Espelhos paralelos: infinitas imagens"
    
    if 360 % n == 0:
        N_theory = int(360 / n) - 1
        formula = f"N = 360°/{n}° - 1 = {N_theory}"
    else:
        N_theory = int(360 / n)
        formula = f"N ≈ 360°/{n}° ≈ {N_theory}"
    
    # Gerar imagens usando algoritmo de reflexão
    images = []
    image_angles = []
    
    # Método: simular reflexões sucessivas
    # Primeiro espelho (eixo X)
    mirror1_angle = 0
    # Segundo espelho
    mirror2_angle = theta
    
    # Usar abordagem sistemática
    generated_positions = set()
    
    # Adicionar objeto real
    generated_positions.add((round(obj_x, 3), round(obj_y, 3)))
    
    # Para cada possível sequência de reflexões
    for sequence_length in range(1, 6):  # até 5 reflexões
        # Gerar todas as sequências binárias (0=espelho1, 1=espelho2)
        sequences = []
        for i in range(2**sequence_length):
            seq = []
            for j in range(sequence_length):
                seq.append((i >> j) & 1)
            sequences.append(seq)
        
        for seq in sequences:
            # Calcular ângulo final após esta sequência
            current_angle = obj_angle
            for mirror in seq:
                if mirror == 0:  # reflexão no espelho 1
                    current_angle = 2 * mirror1_angle - current_angle
                else:  # reflexão no espelho 2
                    current_angle = 2 * mirror2_angle - current_angle
            
            # Normalizar ângulo
            current_angle = current_angle % (2 * np.pi)
            if current_angle > np.pi:
                current_angle -= 2 * np.pi
            
            # Calcular posição
            img_x = obj_radius * np.cos(current_angle)
            img_y = obj_radius * np.sin(current_angle)
            
            # Arredondar para evitar duplicatas por erro numérico
            pos_key = (round(img_x, 3), round(img_y, 3))
            
            if pos_key not in generated_positions:
                generated_positions.add(pos_key)
                images.append((img_x, img_y))
                image_angles.append(current_angle)
    
    # Limitar ao número teórico (para exibição clara)
    if len(images) > N_theory:
        images = images[:N_theory]
    
    return images, image_angles, len(images), formula

def calculate_ray_paths(obj_x, obj_y, images, image_angles):
    """Calcula os caminhos dos raios de luz para algumas imagens"""
    if not show_rays or len(images) == 0:
        return []
    
    ray_paths = []
    
    # Para algumas imagens importantes (primeiras 3)
    for i in range(min(3, len(images))):
        img_x, img_y = images[i]
        
        # Criar caminho simples direto para demonstração
        # Na realidade, o raio refletiria nos espelhos
        # Mas para simplicidade, mostraremos caminho direto
        path_points = [(obj_x, obj_y), (img_x, img_y)]
        ray_paths.append(path_points)
    
    return ray_paths

def update_simulation():
    """Atualiza a simulação com base nos parâmetros atuais"""
    global mirror_lines, obj_point, image_points, image_annotations
    global text_info, ray_lines, formula_text, annotation_text
    
    # Limpar elementos anteriores
    for line in mirror_lines:
        line.remove()
    
    if obj_point:
        obj_point.remove()
    
    for point in image_points:
        point.remove()
    
    # REMOVER ANOTAÇÕES DOS NÚMEROS
    for ann in image_annotations:
        ann.remove()
    image_annotations.clear()  # LIMPAR A LISTA
    
    for line in ray_lines:
        if hasattr(line, 'remove'):
            line.remove()
        elif hasattr(line, 'remove_patch'):
            ax.remove_patch(line)
    
    if text_info:
        text_info.remove()
    
    if formula_text:
        formula_text.remove()
    
    if annotation_text:
        annotation_text.remove()
    
    # Resetar listas
    mirror_lines = []
    image_points = []
    ray_lines = []
    
    # Converter para radianos
    theta = np.radians(theta_deg)
    obj_angle = np.radians(obj_angle_deg)
    
    # Coordenadas do objeto
    obj_x = obj_radius * np.cos(obj_angle)
    obj_y = obj_radius * np.sin(obj_angle)
    
    # Desenhar espelhos
    mirror_length = 5
    mirror1_x = [0, mirror_length]
    mirror1_y = [0, 0]
    mirror1_line, = ax.plot(mirror1_x, mirror1_y, 'b-', linewidth=3, label='Espelho 1')
    mirror_lines.append(mirror1_line)
    
    mirror2_x = [0, mirror_length * np.cos(theta)]
    mirror2_y = [0, mirror_length * np.sin(theta)]
    mirror2_line, = ax.plot(mirror2_x, mirror2_y, 'r-', linewidth=3, label='Espelho 2')
    mirror_lines.append(mirror2_line)
    
    # Desenhar objeto
    obj_point, = ax.plot(obj_x, obj_y, 'go', markersize=15, label='Objeto', 
                        zorder=10, markeredgecolor='black', markeredgewidth=2)
    
    # Calcular e desenhar imagens
    images, image_angles, num_images, formula_str = calculate_images()
    
    for i, (img_x, img_y) in enumerate(images):
        img_point, = ax.plot(img_x, img_y, 'ro', markersize=10, alpha=0.8, 
                           label=f'Imagem {i+1}', zorder=5)
        image_points.append(img_point)
        
        # Anotar número da imagem (AGORA ARMAZENAMOS A REFERÊNCIA)
        offset_x = 0.2 * np.cos(np.arctan2(img_y, img_x))
        offset_y = 0.2 * np.sin(np.arctan2(img_y, img_x))
        ann = ax.annotate(str(i+1), (img_x + offset_x, img_y + offset_y),
                         fontsize=8, color='darkred', fontweight='bold')
        image_annotations.append(ann)  # ADICIONAR À LISTA
    
    # Calcular e desenhar raios de luz se ativado
    if show_rays and len(images) > 0:
        ray_paths = calculate_ray_paths(obj_x, obj_y, images, image_angles)
        
        colors = ['orange', 'purple', 'brown']
        for i, path in enumerate(ray_paths):
            if len(path) > 1:
                # Desenhar linha tracejada para o raio
                x_vals = [p[0] for p in path]
                y_vals = [p[1] for p in path]
                ray_line, = ax.plot(x_vals, y_vals, '--', linewidth=1.5,
                                  color=colors[i % len(colors)], alpha=0.7)
                ray_lines.append(ray_line)
                
                # Adicionar seta
                if len(path) == 2:
                    arrow = FancyArrowPatch(path[0], path[1],
                                          arrowstyle='->', 
                                          color=colors[i % len(colors)],
                                          linewidth=1, alpha=0.7,
                                          mutation_scale=15)
                    ax.add_patch(arrow)
                    ray_lines.append(arrow)
    
    # Adicionar informações
    info_text = f'Ângulo entre espelhos: {theta_deg}°\n'
    info_text += f'Objeto: r={obj_radius:.1f}, θ={obj_angle_deg}°\n'
    info_text += f'Número de imagens: {num_images}\n'
    if theta_deg > 0:
        info_text += f'Fórmula: {formula_str}'
    
    text_info = ax.text(-4.8, -4.8, info_text, fontsize=10,
                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # Adicionar fórmula em destaque
    if theta_deg > 0:
        formula_display = f"Equação dos Espelhos:\n"
        formula_display += r"$N = \frac{360^\circ}{\theta} - 1$" + "\n"
        if 360 % theta_deg == 0:
            formula_display += f"Para θ = {theta_deg}°:\n"
            formula_display += f"N = 360/{theta_deg} - 1 = {int(360/theta_deg)-1}"
        else:
            formula_display += f"Para θ = {theta_deg}°:\n"
            formula_display += f"N ≈ 360/{theta_deg} ≈ {int(360/theta_deg)}"
        
        formula_text = ax.text(3.5, 4.2, formula_display, fontsize=11,
                              bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.9))
    
    # Adicionar anotações explicativas
    if theta_deg > 0:
        explanation = f"Espelho 2 está a {theta_deg}° do Espelho 1\n"
      #  explanation += f"Cada reflexão muda o ângulo em {2*theta_deg}°\n"
      #  explanation += f"Imagens estão a {obj_radius:.1f} unidades da origem"
        
      #  annotation_text = ax.text(3.5, -4.0, explanation, fontsize=9,
       #                         bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
    #
   # ax.legend(loc='upper left', fontsize=9)
  #  fig.canvas.draw_idle()

# Funções de callback
def update_theta(val):
    global theta_deg
    theta_deg = val
    update_simulation()

def update_obj_angle(val):
    global obj_angle_deg
    obj_angle_deg = val
    update_simulation()

def update_obj_radius(val):
    global obj_radius
    obj_radius = val
    update_simulation()

def toggle_rays(label):
    global show_rays
    show_rays = not show_rays
    update_simulation()

def submit_angle(text):
    try:
        angle = float(text)
        if 1 <= angle <= 270:
            slider_theta.set_val(angle)
        else:
            print("Ângulo deve estar entre 1 e 270°")
    except ValueError:
        print("Digite um número válido")

def submit_obj_angle(text):
    try:
        angle = float(text)
        slider_obj_angle.set_val(angle)
    except ValueError:
        print("Digite um número válido")

def submit_obj_radius(text):
    try:
        radius = float(text)
        if radius > 0:
            slider_obj_radius.set_val(radius)
    except ValueError:
        print("Digite um número válido")

# Criar sliders
ax_theta = plt.axes([0.1, 0.22, 0.65, 0.03])
ax_obj_angle = plt.axes([0.1, 0.17, 0.65, 0.03])
ax_obj_radius = plt.axes([0.1, 0.12, 0.65, 0.03])

slider_theta = Slider(ax_theta, 'Ângulo espelhos (°)', 1, 270, valinit=theta_deg)
slider_obj_angle = Slider(ax_obj_angle, 'Ângulo objeto (°)', 0, 360, valinit=obj_angle_deg)
slider_obj_radius = Slider(ax_obj_radius, 'Raio objeto', 0.5, 4.5, valinit=obj_radius)

# Caixas de texto
ax_text_theta = plt.axes([0.78, 0.22, 0.1, 0.03])
ax_text_obj_angle = plt.axes([0.78, 0.17, 0.1, 0.03])
ax_text_obj_radius = plt.axes([0.78, 0.12, 0.1, 0.03])

text_theta = TextBox(ax_text_theta, 'Digite θ:', initial=str(theta_deg))
text_obj_angle = TextBox(ax_text_obj_angle, 'Digite φ:', initial=str(obj_angle_deg))
text_obj_radius = TextBox(ax_text_obj_radius, 'Digite r:', initial=str(obj_radius))

# Checkbuttons para ativar/desativar raios
check_ax = plt.axes([0.78, 0.05, 0.15, 0.04])
check = CheckButtons(check_ax, ['Mostrar Raios'], [show_rays])

# Botão de reset
reset_ax = plt.axes([0.78, 0.27, 0.1, 0.04])
reset_button = Button(reset_ax, 'Reset', color='lightgoldenrodyellow')

# Conectar eventos
slider_theta.on_changed(update_theta)
slider_obj_angle.on_changed(update_obj_angle)
slider_obj_radius.on_changed(update_obj_radius)

text_theta.on_submit(submit_angle)
text_obj_angle.on_submit(submit_obj_angle)
text_obj_radius.on_submit(submit_obj_radius)

check.on_clicked(toggle_rays)

def reset(event):
    slider_theta.set_val(60)
    slider_obj_angle.set_val(30)
    slider_obj_radius.set_val(3.0)
    text_theta.set_val("60")
    text_obj_angle.set_val("30")
    text_obj_radius.set_val("3.0")
    
    # Desativar raios se estiverem ativos
    global show_rays
    if show_rays:
        show_rays = False
        check.set_active(0)
    
    update_simulation()

reset_button.on_clicked(reset)

# Função para arrastar objeto
def on_click(event):
    if event.inaxes == ax:
        x, y = event.xdata, event.ydata
        r = np.sqrt(x**2 + y**2)
        angle = np.degrees(np.arctan2(y, x)) % 360
        
        if 0.5 <= r <= 4.5:
            slider_obj_radius.set_val(r)
        slider_obj_angle.set_val(angle)
        update_simulation()

fig.canvas.mpl_connect('button_press_event', on_click)

# Inicializar simulação
update_simulation()

plt.show()