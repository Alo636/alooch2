import React, {useState, useRef, useEffect} from 'react';
import { User2 } from 'lucide-react';
import MessageBubble from './MessageBubble'; 
import { Send } from 'lucide-react';

// Opcional: puedes añadir aquí otras banderas y nombres de idiomas que quieras soportar
const LANGUAGES = [
  {
    code: 'es',
    name: 'Español',
    flagUrl: 'https://cdn-icons-png.flaticon.com/512/197/197593.png',
    placeholder: "Escribe tu mensaje...",
    send: "Enviar",
    reset: "Reiniciar conversación",
  },
  {
    code: 'en',
    name: 'English',
    flagUrl: 'https://cdn-icons-png.flaticon.com/512/197/197374.png',
    placeholder: "Type your message...",
    send: "Send",
    reset: "Restart conversation",
  },
  {
    code: 'fr',
    name: 'Français',
    flagUrl: 'https://cdn-icons-png.flaticon.com/512/197/197560.png',
    placeholder: "Écris ton message...",
    send: "Envoyer",
    reset: "Redémarrer la conversation",
  },
  {
    code: 'it',
    name: 'Italiano',
    flagUrl: 'https://cdn-icons-png.flaticon.com/512/197/197626.png',
    placeholder: "Scrivi il tuo messaggio...",
    send: "Invia",
    reset: "Riavvia la conversazione",
  },
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

  const messagesEndRef = useRef(null);

  const [languageMenuOpen, setLanguageMenuOpen] = useState(false);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  
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
      const response = await fetch('http://127.0.0.1:8000/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: newUserMessage.content,
          language: language, // Enviamos el idioma seleccionado
          conversation: updatedMessages.map((msg) => ({
            role: msg.role,
            content: msg.content,
          })),
          // user_id: userId
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

  const assistantMessages = messages.filter((msg) => msg.role === 'assistant');
  const shouldDisableAnimation = assistantMessages.length >= 5;

  const inputRef = useRef(null); // 👈 inputRef creado

  useEffect(() => {
    if (!isTyping && inputRef.current) {
      inputRef.current.focus(); // 👈 focus automático
    }
  }, [isTyping]);

  const [restaurantName, setRestaurantName] = useState('Restaurante');
  const [restaurantLogo, setRestaurantLogo] = useState(null);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/restaurant_info")
      .then((res) => res.json())
      .then((data) => {
        if (data.nombre) setRestaurantName(data.nombre);
        if (data.logo_url) setRestaurantLogo(data.logo_url);
      })
      .catch((err) => console.error("Error cargando datos del restaurante:", err));
  }, []);


  return (
    <div
      style={{
        width: '350px',
        height: '500px',
        position: 'fixed',
        bottom: '20px',
        right: '20px',
        backgroundColor: '#fff',
        borderRadius: '12px',
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        fontFamily: 'Arial, sans-serif',
        color: '#111',
        zIndex: 9999,
        fontFamily: 'system-ui, Apple Color Emoji, Segoe UI Emoji, Noto Color Emoji, sans-serif',
      }}
    >

      {/* CABECERA del chat */}
      <div
        style={{
          backgroundColor: '#ffffff',
          boxShadow: 'inset 0 -8px 8px -8px rgba(0, 0, 0, 0.05)', 
          padding: '0.8rem 1rem',
          fontWeight: 'bold',
          fontSize: '1.1rem',
          color: '#111',
          display: 'flex',
          justifyContent: 'space-between', // 👈 nombre a la izquierda, bandera a la derecha
          alignItems: 'center', // 👈 centrado vertical
          position: 'relative',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
          {restaurantLogo && (
            <img
              src={restaurantLogo}
              alt="Logo"
              style={{
                width: '30px',
                height: '30px',
                borderRadius: '50%',
                objectFit: 'cover',
                transform: 'scale(1.4)', // 👈 AGRANDA el logo visualmente
                transformOrigin: 'center',
              }}
            />
          )}
          <span>{restaurantName}</span>
        </div>
        <div
          onClick={() => setLanguageMenuOpen(!languageMenuOpen)}
          style={{
            position: 'absolute',
            right: '15px',
            top: '53%',
            transform: 'translateY(-50%)',
            display: 'flex',
            alignItems: 'center',
            cursor: 'pointer',
            gap: '4px',
          }}
        >
          <img
            src={currentLanguage.flagUrl}
            alt={currentLanguage.name}
            style={{
              width: '18px',
              height: '18px',
              borderRadius: '50%',
              objectFit: 'cover',
              display: 'block',
            }}
          />
          <span style={{ fontSize: '0.8rem', color: '#333',lineHeight: 1,position: 'relative', top: '-5px', // 👈 leve ajuste vertical 
          }}>⌄</span>
        </div>

        {/* Menú desplegable de banderas */}
        {languageMenuOpen && (
          <div
            style={{
              position: 'absolute',
              right: '10px',
              top: 'calc(100% + 5px)',
              backgroundColor: '#fff',
              border: '1px solid #ccc',
              borderRadius: '5px',
              boxShadow: '0 2px 5px rgba(0,0,0,0.2)',
              zIndex: 10,
            }}
          >
            {LANGUAGES.map((lang) => (
              <div
                key={lang.code}
                onClick={() => {
                  setLanguage(lang.code);
                  setLanguageMenuOpen(false);
                }}
                style={{
                  padding: '5px 10px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                }}
              >
                <img
                  src={lang.flagUrl}
                  alt={lang.name}
                  style={{
                    width: '20px',
                    height: '20px',
                    borderRadius: '50%',
                    objectFit: 'cover',
                    display: 'block',
                  }}
                />
                <span style={{ fontSize: '0.9rem', color: '#000' }}>{lang.name}</span>
              </div>
            ))}
          </div>
        )}

      </div>
        {/* CONTENEDOR DE MENSAJES */}
        <div
          style={{
            position: 'relative',
            borderRadius: '8px',
            padding: '1rem',
            height: '300px',
            overflowY: 'auto',
            marginBottom: '1rem',
            backgroundColor: '#fff',
            display: 'flex',
            flexDirection: 'column',
            boxShadow: 'inset 0 -8px 8px -8px rgba(0, 0, 0, 0.05)', 
          }}
        >
          {messages.map((msg, index) => {
            const previousMsg = messages[index - 1];
            const sameSender = previousMsg && previousMsg.role === msg.role;

            return (
              <div
                key={index}
                style={{
                  marginTop: sameSender ? '4px' : '12px',
                  display: 'flex',
                  justifyContent: msg.role === 'assistant' ? 'flex-start' : 'flex-end',
                }}
              >
                <MessageBubble
                  role={msg.role}
                  content={msg.content}
                  disableAnimation={shouldDisableAnimation}
                  animationDelay={`${index * 0.05}s`} // 👈 le pasas el delay como prop
                />

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
            );
          })}

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
                  padding: '6px 10px',
                  borderRadius: '15px',
                  display: 'inline-flex', // 👈 en lugar de flex
                  alignItems: 'center',
                  boxShadow: '0 1px 3px rgba(0,0,0,0.2)',
                  border: '1px solid #ccc',
                }}
              >
                <div style={{ display: 'flex', gap: '4px', alignItems: 'center', height: '16px' }}>
                  <div
                    style={{
                      width: '6px',
                      height: '6px',
                      backgroundColor: '#888',
                      borderRadius: '50%',
                      animation: 'bounce 1.4s infinite',
                      animationDelay: '0s',
                    }}
                  />
                  <div
                    style={{
                      width: '6px',
                      height: '6px',
                      backgroundColor: '#888',
                      borderRadius: '50%',
                      animation: 'bounce 1.4s infinite',
                      animationDelay: '0.2s',
                    }}
                  />
                  <div
                    style={{
                      width: '6px',
                      height: '6px',
                      backgroundColor: '#888',
                      borderRadius: '50%',
                      animation: 'bounce 1.4s infinite',
                      animationDelay: '0.4s',
                    }}
                  />
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
    
      {/* INPUT Y BOTÓN ENVIAR */}
      <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
      <input
        ref={inputRef}
        style={{
          flex: 1,
          padding: '0.5rem',
          borderRadius: '5px',
          marginLeft: '4px', 
          border: '1px solid #ccc',
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
          if (e.key === 'Enter' && !isTyping) handleSendMessage();
        }}
        placeholder={currentLanguage.placeholder}
        disabled={isTyping}
        readOnly={isTyping}
      />
        <button
          style={{
            backgroundColor: isTyping ? '#aaa' : '#73b6ff',
            color: '#fff',
            border: 'none',
            borderRadius: '50%',
            marginRight: '5px', 
            width: '35px',
            height: '35px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '1.2rem',
            cursor: isTyping ? 'not-allowed' : 'pointer',
            boxShadow: '0 1px 3px rgba(0,0,0,0.2)',
            transition: 'background-color 0.3s ease',
          }}
          onClick={handleSendMessage}
          disabled={isTyping}
          title={currentLanguage.send} // tooltip al pasar el mouse
        >
          <Send size={20} color="black" />
        </button>
      </div>

      {/* BOTÓN PARA REINICIAR CONVERSACIÓN */}
      <button
        style={{
          marginTop: '1rem',
          backgroundColor: '#fffffffff',
          color: '#111',
          border: '1px solid #ccc',
          borderRadius: '6px',
          padding: '0.75rem 1rem',
          cursor: 'pointer',
          fontSize: '0.9rem',
          transition: 'background-color 0.3s ease',
          fontFamily: 'inherit',
        }}
        onClick={() => setMessages([])}
        onMouseEnter={(e) => {
          e.target.style.backgroundColor = '#f2f2f2';
        }}
        onMouseLeave={(e) => {
          e.target.style.backgroundColor = '#ffffff';
        }}
      >
        {currentLanguage.reset}
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
      @keyframes bounce {
        0%, 80%, 100% {
          transform: translateY(0);
        }
        40% {
          transform: translateY(-5px); /* 👈 Más pequeño para no salir de la burbuja */
        }
      }
      `}
      </style>
    </div>
  );
};

export default ChatBotUI;