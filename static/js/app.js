let sessionId = 'session_' + Date.now();
let showHistory = false;

function addMessage(text, isUser = false) {
    const container = document.getElementById('chatContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'ai-message'}`;
    messageDiv.textContent = text;
    container.appendChild(messageDiv);
    container.scrollTop = container.scrollHeight;
}

function showLoading(show) {
    document.getElementById('loading').classList.toggle('active', show);
}

function formatLLMResponse(text) {
    if (!text || typeof text !== 'string') return '';
    
    let formatted = text;
    
    // 1. Convertir **texto** a <strong> con estilo personalizado
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong class="ai-bold">$1</strong>');
    
    // 2. Convertir *texto* a <em> (cursiva)
    formatted = formatted.replace(/\*(.*?)\*/g, '<em class="ai-italic">$1</em>');
    
    // 3. Convertir encabezados markdown
    formatted = formatted.replace(/^### (.*$)/gm, '<h4 class="ai-h4">$1</h4>');
    formatted = formatted.replace(/^## (.*$)/gm, '<h3 class="ai-h3">$1</h3>');
    formatted = formatted.replace(/^# (.*$)/gm, '<h2 class="ai-h2">$1</h2>');
    
    // 4. Convertir listas con •, -, o números
    // Para listas con viñetas
    formatted = formatted.replace(/^[•\-] (.*$)/gm, '<li class="ai-li">$1</li>');
    
    // Para listas numeradas (1., 2., etc.)
    formatted = formatted.replace(/^(\d+)\. (.*$)/gm, '<li class="ai-li numbered"><span class="number">$1.</span> $2</li>');
    
    // 5. Manejar párrafos y saltos de línea
    const lines = formatted.split('\n');
    let result = [];
    let inList = false;
    let listItems = [];
    
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        
        if (!line) continue; // Saltar líneas vacías
        
        // Si es un elemento de lista
        if (line.startsWith('<li')) {
            if (!inList) {
                inList = true;
                // Determinar si es lista numerada
                const isNumbered = line.includes('numbered');
                result.push(isNumbered ? '<ol class="ai-list">' : '<ul class="ai-list">');
            }
            result.push(line);
            
            // Verificar si la siguiente línea también es lista
            const nextLine = i + 1 < lines.length ? lines[i + 1].trim() : '';
            if (!nextLine.startsWith('<li')) {
                result.push(inList ? '</ul>' : '</ol>');
                inList = false;
            }
        } 
        // Si es un encabezado
        else if (line.startsWith('<h')) {
            if (inList) {
                result.push('</ul>');
                inList = false;
            }
            result.push(line);
        }
        // Si es texto normal
        else {
            if (inList) {
                result.push('</ul>');
                inList = false;
            }
            // Solo agregar <p> si no está vacío y no es HTML ya
            if (line && !line.startsWith('<')) {
                result.push(`<p class="ai-p">${line}</p>`);
            } else if (line) {
                result.push(line);
            }
        }
    }
    
    // Cerrar lista si queda abierta
    if (inList) {
        result.push('</ul>');
    }
    
    formatted = result.join('\n');
    
    // 6. Convertir saltos de línea simples a <br>
    formatted = formatted.replace(/\n/g, '<br>');
    
    // 7. Limpiar HTML duplicado
    formatted = formatted.replace(/<br><br>/g, '<br>');
    formatted = formatted.replace(/<p><\/p>/g, '');
    
    return formatted;
}

function addFormattedMessage(text, isUser = false) {
    const container = document.getElementById('chatContainer');
    const messageDiv = document.createElement('div');
    
    messageDiv.className = `message ${isUser ? 'user-message' : 'ai-message'}`;
    
    if (isUser) {
        // Mensajes del usuario sin formateo
        messageDiv.textContent = text;
    } else {
        // Mensajes del AI con formateo
        messageDiv.innerHTML = formatLLMResponse(text);
        // Añadir clase adicional para estilos específicos
        messageDiv.classList.add('ai-formatted');
    }
    
    container.appendChild(messageDiv);
    container.scrollTop = container.scrollHeight;
}


async function sendMessage() {
    const input = document.getElementById('queryInput');
    const text = input.value.trim();
    const btn = document.getElementById('sendBtn');
    
    if (!text) return;
    
    // Mostrar mensaje del usuario
    addFormattedMessage(text, true);
    input.value = '';
    btn.disabled = true;
    showLoading(true);
    
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: text,
                session_id: sessionId
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Mostrar respuesta de la IA
            addFormattedMessage(data.response);

        } else {
            addFormattedMessage(`Error: ${data.error || 'Error desconocido'}`);
        }
    } catch (error) {
        addFormattedMessage(`Error de conexión: ${error.message}`);
    } finally {
        btn.disabled = false;
        showLoading(false);
    }
}

async function toggleHistory() {
    const panel = document.getElementById('historyPanel');
    showHistory = !showHistory;
    
    if (showHistory) {
        panel.classList.add('active');
        await loadHistory();
    } else {
        panel.classList.remove('active');
    }
}

async function loadHistory() {
    const panel = document.getElementById('historyPanel');
    panel.innerHTML = '<div style="text-align: center; padding: 20px; color: #6b7280;">Cargando historial...</div>';
    
    try {
        const response = await fetch(`/history?session_id=${sessionId}&limit=20`);
        const data = await response.json();
        
        if (response.ok && data.history.length > 0) {
            panel.innerHTML = data.history.map(item => `
                <div class="history-item">
                    <strong>❓ Pregunta:</strong> ${item.user_query.substring(0, 100)}${item.user_query.length > 100 ? '...' : ''}<br>
                    <strong>🤖 Respuesta:</strong> ${item.llm_response.substring(0, 100)}${item.llm_response.length > 100 ? '...' : ''}<br>
                    <small>📅 ${new Date(item.created_at).toLocaleString()}</small>
                </div>
            `).join('');
        } else {
            panel.innerHTML = '<div style="text-align: center; padding: 20px; color: #6b7280;">No hay historial aún</div>';
        }
    } catch (error) {
        panel.innerHTML = `<div style="color: #ef4444;">Error cargando historial</div>`;
    }
}

// Inicializar con un mensaje de bienvenida
window.onload = function() {
    addFormattedMessage("¡Hola! Soy tu organizador de viajes. ¿En qué puedo ayudarte hoy?");
};