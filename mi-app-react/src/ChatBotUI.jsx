import React, { useState, useEffect } from 'react';

{/* Icono de bandera redonda al lado del "nombre" (Título) */}

// Opcional: puedes añadir aquí otras banderas y nombres de idiomas que quieras soportar
const LANGUAGES = [
  {
    code: 'es',
    name: 'Español',
    flagUrl: 'https://cdn-icons-png.flaticon.com/512/197/197593.png', // Bandera de España
  },
  {
    code: 'en',
    name: 'English',
    flagUrl: 'https://cdn-icons-png.flaticon.com/512/197/197374.png', // Bandera (EE.UU./Inglaterra)
  },
  {
    code: 'fr',
    name: 'Français',
    flagUrl: 'https://cdn-icons-png.flaticon.com/512/197/197560.png', // Bandera de Francia
  },
  {
    code: 'it',
    name: 'Italiano',
    flagUrl: 'https://cdn-icons-png.flaticon.com/512/197/197626.png', // Bandera de Italia
  },
  // Agrega más si lo deseas
];

const ChatBotUI = () => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [selectedImage, setSelectedImage] = useState(null);
  const [isTyping, setIsTyping] = useState(false);

  // Estado para el idioma seleccionado
  const [language, setLanguage] = useState('es');

  // Función para encontrar el objeto de idioma actualmente seleccionado
  const currentLanguage = LANGUAGES.find((lang) => lang.code === language);

  const handleSendMessage = async () => {
    // Evitar enviar mensajes vacíos
    if (!inputValue.trim()) return;

    // Crear el objeto del mensaje del usuario
    const newUserMessage = { role: 'user', content: inputValue };

    // Limpiar el input y mostrar "escribiendo..."
    setInputValue('');
    setIsTyping(true);

    // Crear un array con el historial actualizado
    const updatedMessages = [...messages, newUserMessage];
    // Actualizar el estado con el nuevo mensaje del usuario
    setMessages(updatedMessages);

    try {
      // Hacer la petición con el historial ACTUALIZADO y el idioma seleccionado
      const response = await fetch('http://localhost:8000/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: newUserMessage.content,
          language: language, // Enviamos el idioma seleccionado
          conversation: updatedMessages.map((msg) => ({
            role: msg.role,
            content: msg.content,
          })),
        }),
      });

      if (!response.ok) {
        throw new Error(`Error en la respuesta del servidor: ${response.status}`);
      }

      const data = await response.json();
      if (!data || !data.answer) throw new Error('Respuesta vacía del servidor');

      // Revisar si la respuesta contiene una URL de imagen
      const imageRegex = /(https?:\/\/.*\.(?:png|jpg|jpeg|gif|webp))/i;
      const match = data.answer.match(imageRegex);

      // Construimos el mensaje del bot, separando texto e imagen (si aplica)
      let botMessage = { role: 'assistant', content: data.answer };
      if (match) {
        const imageUrl = match[0];
        const contentWithoutImage = data.answer.replace(imageUrl, '').trim();
        botMessage = {
          role: 'assistant',
          content: contentWithoutImage,
          imageUrl,
        };
      }

      // Dividir el contenido del mensaje en partes lógicas
      const messageParts = splitMessage(botMessage.content, 200);

      // Simular envío de cada parte con ligera pausa
      for (let i = 0; i < messageParts.length; i++) {
        // Esperar un tiempo para simular escritura
        await new Promise((resolve) => setTimeout(resolve, i * 1000));

        // Si existe una imagen en botMessage, se adjunta al primer fragmento
        if (i === 0 && botMessage.imageUrl) {
          setMessages((prev) => [
            ...prev,
            {
              role: 'assistant',
              content: messageParts[i],
              imageUrl: botMessage.imageUrl,
            },
          ]);
        } else {
          setMessages((prev) => [
            ...prev,
            { role: 'assistant', content: messageParts[i] },
          ]);
        }
      }
    } catch (error) {
      console.error('Error al conectar con el servidor:', error);
      // Añadimos un mensaje de error en el chat
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Error al contactar el servidor.',
        },
      ]);
    } finally {
      setIsTyping(false);
    }
  };

  /**
   * Función para dividir el mensaje en partes de longitud máxima maxLength
   * procurando no partir frases por la mitad.
   */
  const splitMessage = (text, maxLength) => {
    if (!text) return ['']; // Control por si llega un texto vacío
    const parts = [];
    let tempMessage = text;

    while (tempMessage.length > maxLength) {
      // Buscar un punto de corte (punto, interrogación o salto de línea) antes de maxLength
      let splitIndex = Math.max(
        tempMessage.lastIndexOf('. ', maxLength),
        tempMessage.lastIndexOf('? ', maxLength),
        tempMessage.lastIndexOf('\n', maxLength)
      );

      // Si no encuentra un punto adecuado, forzamos el corte
      if (splitIndex === -1 || splitIndex < maxLength * 0.5) {
        splitIndex = maxLength;
      }

      parts.push(tempMessage.substring(0, splitIndex + 1).trim());
      tempMessage = tempMessage.substring(splitIndex + 1).trim();
    }

    // Agregar la última parte si quedó texto pendiente
    if (tempMessage.length > 0) {
      parts.push(tempMessage);
    }

    return parts;
  };

  // Función para abrir la imagen en un modal
  const openImageModal = (imageUrl) => {
    setSelectedImage(imageUrl);
  };

  // Función para cerrar el modal
  const closeModal = () => {
    setSelectedImage(null);
  };

  return (
    <div
      style={{
        maxWidth: '600px',
        margin: '0 auto',
        marginTop: '2rem',
        backgroundColor: '#fff', // Fondo blanco
        borderRadius: '10px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.2)',
        padding: '2rem',
        fontFamily: 'Georgia, serif',
        color: '#000', // Texto en negro
      }}
    >
      {/* CONTENEDOR DE TÍTULO + SELECCIÓN DE IDIOMA */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          marginBottom: '1.5rem',
        }}
      >
        <h1
          style={{
            textAlign: 'center',
            fontSize: '1.8rem',
            margin: 0,
            letterSpacing: '1px',
            color: '#000',
          }}
        >
          Chat en Blanco y Negro
        </h1>
      </div>

      {/* MENÚ DESPLEGABLE PARA CAMBIAR DE IDIOMA CON BANDERA */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center', // Alineación vertical centrada
          justifyContent: 'center',
          gap: '10px',
          marginBottom: '1.5rem',
        }}
      >
        {/* Bandera */}
        {currentLanguage && (
          <img
            src={currentLanguage.flagUrl}
            alt={`Bandera de ${currentLanguage.name}`}
            style={{
              width: '30px',
              height: '30px',
              borderRadius: '50%',
              boxShadow: '0 1px 3px rgba(0,0,0,0.3)',
              border: '1px solid #000',
              objectFit: 'cover',
            }}
          />
        )}

        {/* Select de idiomas */}
        <select
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          style={{
            padding: '0.5rem',
            borderRadius: '5px',
            border: '1px solid #000',
            backgroundColor: '#fff',
            fontSize: '1rem',
            fontFamily: 'inherit',
          }}
        >
          {LANGUAGES.map((lang) => (
            <option key={lang.code} value={lang.code}>
              {lang.name}
            </option>
          ))}
        </select>
      </div>


      {/* CONTENEDOR DE MENSAJES */}
      <div
        style={{
          borderRadius: '8px',
          padding: '1rem',
          height: '300px',
          overflowY: 'auto',
          marginBottom: '1rem',
          backgroundColor: '#fff',
          display: 'flex',
          flexDirection: 'column',
          border: '1px solid #000',
        }}
      >
        {messages.map((msg, index) => (
          <div
            key={index}
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems:
                msg.role === 'assistant' ? 'flex-start' : 'flex-end',
              marginBottom: '0.8rem',
            }}
          >
            {/* Contenido de texto */}
            {msg.content && (
              <div
                style={{
                  // Distinguimos el color según sea el user o el asistente
                  backgroundColor:
                    msg.role === 'assistant' ? '#f8f8f8' : '#000',
                  color: msg.role === 'assistant' ? '#000' : '#fff',
                  padding: '0.6rem 1rem',
                  borderRadius: '15px',
                  maxWidth: '70%',
                  minHeight: '35px',
                  display: 'flex',
                  alignItems: 'center',
                  whiteSpace: 'pre-wrap',
                  boxShadow: '0 1px 3px rgba(0,0,0,0.2)',
                  // Añadimos un pequeño borde para estilo
                  border:
                    msg.role === 'assistant'
                      ? '1px solid #ccc'
                      : '1px solid #000',
                }}
              >
                {msg.content}
              </div>
            )}

            {/* Imagen adjunta (si existe) */}
            {msg.imageUrl && (
              <img
                src={msg.imageUrl}
                alt="Imagen del bot"
                style={{
                  marginTop: '0.5rem',
                  width: '180px',
                  height: '180px',
                  borderRadius: '10px',
                  objectFit: 'cover',
                  cursor: 'pointer',
                  boxShadow: '0 2px 5px rgba(0,0,0,0.3)',
                  border: '1px solid #000',
                }}
                onClick={() => openImageModal(msg.imageUrl)}
              />
            )}
          </div>
        ))}

        {/* Burbuja de "escribiendo..." */}
        {isTyping && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'flex-start',
              marginLeft: '10px',
            }}
          >
            <div
              style={{
                backgroundColor: '#f8f8f8',
                padding: '10px 15px',
                borderRadius: '15px',
                display: 'flex',
                alignItems: 'center',
                minWidth: '50px',
                maxWidth: '80px',
                boxShadow: '0 1px 3px rgba(0,0,0,0.2)',
                border: '1px solid #ccc',
              }}
            >
              <div style={{ display: 'flex', gap: '5px' }}>
                <div
                  style={{
                    width: '8px',
                    height: '8px',
                    backgroundColor: '#000',
                    borderRadius: '50%',
                    animation: 'typingAnimation 1.5s infinite ease-in-out',
                    animationDelay: '0s',
                  }}
                />
                <div
                  style={{
                    width: '8px',
                    height: '8px',
                    backgroundColor: '#000',
                    borderRadius: '50%',
                    animation: 'typingAnimation 1.5s infinite ease-in-out',
                    animationDelay: '0.2s',
                  }}
                />
                <div
                  style={{
                    width: '8px',
                    height: '8px',
                    backgroundColor: '#000',
                    borderRadius: '50%',
                    animation: 'typingAnimation 1.5s infinite ease-in-out',
                    animationDelay: '0.4s',
                  }}
                />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* INPUT Y BOTÓN ENVIAR */}
      <div style={{ display: 'flex', gap: '0.5rem' }}>
        <input
          style={{
            flex: 1,
            padding: '0.75rem',
            borderRadius: '6px',
            border: '1px solid #000',
            outline: 'none',
            fontSize: '1rem',
            fontFamily: 'inherit',
            color: '#000',
            backgroundColor: '#fff',
          }}
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={(e) => {
            if (e.key === 'Enter') handleSendMessage();
          }}
          placeholder="Escribe tu mensaje..."
        />
        <button
          style={{
            backgroundColor: '#000',
            color: '#fff',
            border: 'none',
            borderRadius: '6px',
            padding: '0 1rem',
            cursor: 'pointer',
            fontSize: '1rem',
            fontWeight: 'bold',
            boxShadow: '0 1px 3px rgba(0,0,0,0.2)',
            transition: 'background-color 0.3s ease',
            fontFamily: 'inherit',
          }}
          onClick={handleSendMessage}
          onMouseEnter={(e) => (e.target.style.backgroundColor = '#333')}
          onMouseLeave={(e) => (e.target.style.backgroundColor = '#000')}
        >
          Enviar
        </button>
      </div>

      {/* BOTÓN PARA REINICIAR CONVERSACIÓN */}
      <button
        style={{
          marginTop: '1rem',
          backgroundColor: '#fff',
          color: '#000',
          border: '1px solid #000',
          borderRadius: '6px',
          padding: '0.5rem 1rem',
          cursor: 'pointer',
          fontSize: '0.9rem',
          transition: 'all 0.3s ease',
          fontFamily: 'inherit',
        }}
        onClick={() => setMessages([])}
        onMouseEnter={(e) => {
          e.target.style.backgroundColor = '#f0f0f0';
        }}
        onMouseLeave={(e) => {
          e.target.style.backgroundColor = '#fff';
        }}
      >
        Reiniciar conversación
      </button>

      {/* MODAL PARA MOSTRAR IMAGEN AMPLIADA */}
      {selectedImage && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0,0,0,0.5)',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            zIndex: 999,
          }}
          onClick={closeModal}
        >
          <img
            src={selectedImage}
            alt="Imagen ampliada"
            style={{
              maxWidth: '80%',
              maxHeight: '80%',
              borderRadius: '8px',
              boxShadow: '0 2px 10px rgba(0,0,0,0.5)',
              border: '1px solid #fff',
            }}
          />
        </div>
      )}

      {/* Estilos para la animación de los tres puntitos */}
      <style>
        {`
          @keyframes typingAnimation{
            0% { opacity: 0.2; }
            50% { opacity: 1; }
            100% { opacity: 0.2; }
          }
        `}
      </style>
    </div>
  );
};

export default ChatBotUI;