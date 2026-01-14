🧳 Travel Chat Assistant

**TripOrganizer** es un asistente especializado en planificación de viajes que combina inteligencia artificial con conocimiento experto en turismo para ofrecer recomendaciones personalizadas y detalladas. 
Diseñado tanto para **viajeros ocasionales** que buscan inspiración como para **exploradores frecuentes** que necesitan optimizar itinerarios, la aplicación analiza preferencias individuales para sugerir destinos, rutas, alojamientos y experiencias gastronómicas auténticas. 
Promete simplificar la complejidad de la organización de viajes mediante respuestas inmediatas, eliminando la necesidad de consultar múltiples fuentes y adaptándose a presupuestos, intereses específicos y restricciones de tiempo. Ideal para **agentes de viajes** que buscan una herramienta de apoyo, **estudiantes** planeando mochileos, **familias** organizando vacaciones y **profesionales** que necesitan planificar viajes de negocios eficientes, TripOrganizer garantiza una experiencia de usuario intuitiva mientras aprende de cada interacción para refinar sus recomendaciones futuras.
## ✨ Características

*  🤖 **Asistente especializado en viajes**: Respuestas enfocadas en turismo, transporte, gastronomía, cultura y alojamiento
    
*   💾 **Historial persistente**: Guarda todas las conversaciones en PostgreSQL
    
*   🚀 **Respuestas rápidas**: Utiliza modelos LLM de Groq (openai/gpt-oss-20b)
    
*   🌐 **Interfaz web moderna**: Chat interactivo con diseño responsive
    
*   🔒 **Manejo de sesiones**: Historial separado por sesiones de usuario

## 📁 Estructura del Proyecto

- app.py   📌 # Aplicación principal Flask
- requirements.txt    🧩# Dependencias de Python
- .env       🧩# Variables de entorno
- .gitignore         🧩# Archivos ignorados por git
- templates/index.html    📌 # Interfaz web del chat
- docker-compose.yaml	🧩# fichero para desplegar toda la app
- Dockerfile	🧩#la "receta" para crear la imagen Docker de la app
- render.yaml		🧩#configuracion para desplegar en Render
- test_app.py	✔️#test automatizados para verificar las api
-  static/css/ style.css     ➡️ # Estilos CSS
- static/js/app.js    ➡️# Lógica del chat en frontend
-  static/images	    ➡️# Las imágenes usadas

# 🛠️ Herramientas y Tecnologías

El desarrollo de TripOrganizer ha sido posible gracias a un **stack tecnológico moderno y robusto** que combina inteligencia artificial con desarrollo web de última generación:

-   **Python** 🐍 como lenguaje principal para la lógica del servidor y automatizaciones.
    
-   **Flask** 🌶️ como framework web ligero y eficiente para construir la API RESTful y servir la interfaz.
    
-   **Groq** ⚡ como plataforma de inferencia ultrarrápida para acceder a modelos LLM de última generación.
    
-   **PostgreSQL** 🐘 como sistema de base de datos relacional para almacenamiento persistente del historial.
    
-   **Render** 🚀 como plataforma de despliegue cloud para hosting y escalabilidad automática.
    
-   **Docker** 🐳 para contenerización y despliegue consistente en cualquier entorno.
    
-   **Modelos LLM avanzados** (OpenAi) 🤖 que proporcionan respuestas contextuales y conocimiento experto en viajes.
    

Esta combinación de herramientas permite una **arquitectura modular, escalable y mantenible**, donde cada componente se integra eficientemente para ofrecer una experiencia de usuario fluida y respuestas de alta calidad en tiempo real.

## 📞 Contacto
-   Autor: Balirina
    
_________

## 📌 Acceso a la app
https://trip-organizer-hvck.onrender.com

¿Listo para planear tu próximo viaje? 🗺️✈️🏨