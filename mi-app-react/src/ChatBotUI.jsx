import React, {useState, useRef, useEffect} from 'react';
import MessageBubble from './MessageBubble'; 
import { Send, ChevronDown, MoreVertical, RotateCcw, User2, MessageCircle } from 'lucide-react';
import Zoom from 'react-medium-image-zoom';
import 'react-medium-image-zoom/dist/styles.css';
import { useIsMobile } from './hooks/useIsMobile';  // asegúrate de ponerlo en la ruta correcta
import './ChatBotUI.css';



// Opcional: puedes añadir aquí otras banderas y nombres de idiomas que quieras soportar
const LANGUAGES = [
  {
    code: 'es',
    name: 'Español',
    flagUrl: 'https://cdn-icons-png.flaticon.com/512/197/197593.png',
    placeholder: "Escribe tu mensaje...",
    send: "Enviar",
    reset: "Reiniciar",
  },
  {
    code: 'en',
    name: 'English',
    flagUrl: 'https://cdn-icons-png.flaticon.com/512/197/197374.png',
    placeholder: "Type your message...",
    send: "Send",
    reset: "Restart",
  },
  {
    code: 'fr',
    name: 'Français',
    flagUrl: 'https://cdn-icons-png.flaticon.com/512/197/197560.png',
    placeholder: "Écris ton message...",
    send: "Envoyer",
    reset: "Redémarrer",
  },
  {
    code: 'it',
    name: 'Italiano',
    flagUrl: 'https://cdn-icons-png.flaticon.com/512/197/197626.png',
    placeholder: "Scrivi il tuo messaggio...",
    send: "Invia",
    reset: "Riavvia",
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
    if (!inputValue.trim()) return;
  
    const newUserMessage = { role: 'user', content: inputValue };
    setInputValue('');
    setIsTyping(true);
    cancelTyping.current = false;
  
    const updatedMessages = [...messages, newUserMessage];
    setMessages(updatedMessages);
  
    // 👉 Crear un AbortController nuevo
    const controller = new AbortController();
    abortControllerRef.current = controller;
  
    try {
      const response = await fetch('http://127.0.0.1:8000/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: newUserMessage.content,
          language: language,
          conversation: updatedMessages.map((msg) => ({
            role: msg.role,
            content: msg.content,
          })),
        }),
        signal: controller.signal, // 👈 Vincular signal
      });
  
      if (!response.ok) {
        throw new Error(`Error en la respuesta del servidor: ${response.status}`);
      }
  
      const data = await response.json();
      if (!data || !data.answer) throw new Error('Respuesta vacía del servidor');
  
      const imageRegex = /(https?:\/\/.*\.(?:png|jpg|jpeg|gif|webp))/i;
      const match = data.answer.match(imageRegex);
  
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
  
      const messageParts = splitMessage(botMessage.content, 200);
  
      for (let i = 0; i < messageParts.length; i++) {
        if (cancelTyping.current) break;
  
        await new Promise((resolve) => setTimeout(resolve, i * 1000));
  
        if (cancelTyping.current) break;
  
        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            content: messageParts[i],
            ...(i === 0 && botMessage.imageUrl ? { imageUrl: botMessage.imageUrl } : {}),
          },
        ]);
      }
    } catch (error) {
      if (error.name === 'AbortError') {
        console.log('Petición abortada correctamente.');
        return;
      }
      console.error('Error al conectar con el servidor:', error);
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

  const cancelTyping = useRef(false);
  const abortControllerRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        !event.target.closest('.language-menu-button') &&
        !event.target.closest('.language-menu-dropdown')&&
        !event.target.closest('.options-menu-button') &&
        !event.target.closest('.options-menu-dropdown')
      ) {
        setLanguageMenuOpen(false);
        setOptionsMenuOpen(false);
      }
    };
    document.addEventListener('click', handleClickOutside);
    return () => {
      document.removeEventListener('click', handleClickOutside);
    };
  }, []);

  const isMobile = useIsMobile();

  const [isChatOpen, setIsChatOpen] = useState(true);

  const [optionsMenuOpen, setOptionsMenuOpen] = useState(false);

  const menuButtons = [
    {
      key: 'language',
      title: currentLanguage.name,
      icon: (
        <img
          src={currentLanguage.flagUrl}
          alt={currentLanguage.name}
          style={{ width: '18px', height: '18px', borderRadius: '50%' }}
        />
      ),
      onClick: () => setLanguageMenuOpen(!languageMenuOpen),
    },
    {
      key: 'reset',
      title: currentLanguage.reset,
      icon: <RotateCcw size={18} color="#444" />,
      onClick: () => {
        if (abortControllerRef.current) abortControllerRef.current.abort();
        cancelTyping.current = true;
        setIsTyping(false);
        setMessages([]);
        setTimeout(() => {
          cancelTyping.current = false;
          abortControllerRef.current = null;
        }, 200);
      },
    },
  ];  
  

  return (
    <>
      {isChatOpen ? (
        <div className="chatbot-container" style={{
          width: '100%',
          maxWidth: '350px', // en lugar de width fijo
          height: '60vh',    // en lugar de height fijo
          maxHeight: '515px',
          position: 'fixed',
          bottom: '20px',
          right: '20px',
          backgroundColor: '#fff',
          borderRadius: '25px',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          color: '#111',
          zIndex: 9999,
        }}>
          {/* CABECERA del chat */}
            <div
              style={{
                backgroundColor: '#ffffff',
                padding: '1.1rem 1.3rem',
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
                <span className="restaurant-name">{restaurantName}</span>
              </div>
              <button
              onClick={e => { e.stopPropagation(); setOptionsMenuOpen(o => !o); }}
              style={{
                all: 'unset',
                cursor: 'pointer',
                padding: 4,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginLeft: 70
              }}
              title="Opciones"
            >
              <MoreVertical size={18} color="#000" />
            </button>
            {optionsMenuOpen && (
              <div
              className="options-menu-dropdown"
              onClick={(e) => e.stopPropagation()}
              style={{
                position: 'absolute',
                top: '100%',
                right: 70,
                backgroundColor: '#fff',
                border: '1px solid #ccc',
                borderRadius: 5,
                boxShadow: '0 2px 5px rgba(0,0,0,0.2)',
                zIndex: 1000,
                padding: '12px',
                display: 'flex',
                flexDirection: 'column',
                gap: '12px',
              }}
            >
              {/* Bloque idioma */}
              <button
                className="menu-item" 
                onClick={() => setLanguageMenuOpen(!languageMenuOpen)}>
                <div
                style={{
                  all: 'unset',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                }}
              >
                <img
                  src={currentLanguage.flagUrl}
                  alt={currentLanguage.name}
                  style={{ width: '18px', height: '18px', borderRadius: '50%' }}
                />
                <span style={{ display: 'flex', alignItems: 'center', gap: '4px', }}>{currentLanguage.name}</span>
                <span style={{ fontSize: '0.7rem', alignSelf: 'center', position: 'relative', top: '-3px', right: '4px' }}>⌄</span>
                </div>
              </button>

              {/* Bloque reinicio */}
              <button
                className="menu-item" 
                onClick={() => {
                  if (abortControllerRef.current) abortControllerRef.current.abort();
                  cancelTyping.current = true;
                  setIsTyping(false);
                  setMessages([]);
                  setTimeout(() => {
                    cancelTyping.current = false;
                    abortControllerRef.current = null;
                  }, 200);
                }}
                style={{
                  all: 'unset',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  transition: 'opacity 0.2s ease',
                }}
                title={currentLanguage.reset}
                aria-label={currentLanguage.reset}
              >
                <RotateCcw size={18} />
                <span style={{ fontSize: '0.8rem', }}>{currentLanguage.reset}</span>
              </button>
            
              {/* Menú desplegable de banderas */}
              {languageMenuOpen && (
                <div
                  className="language-menu-dropdown"
                  onClick={() => setLanguageMenuOpen(!languageMenuOpen)}
                  style={{
                    position: 'absolute',
                    right: '10px',
                    top: 'calc(100% + 5px)',
                    backgroundColor: '#fff',
                    border: '1px solid #ccc',
                    borderRadius: '5px',
                    boxShadow: '0 2px 5px rgba(0,0,0,0.2)',
                    zIndex: 30,
                    opacity: 1, 
                    transition: 'opacity 0.3s ease',
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
                      <span style={{ fontSize: '0.9rem', color: '#000', }}>{lang.name}</span>
                    </div>
                  ))}
                </div>
              )}
              </div>
            )}
            {/* Flecha hacia abajo para minimizar */}
            <button
              onClick={() => setIsChatOpen(false)}
              style={{ all: 'unset', cursor: 'pointer', padding: 4, borderRadius: '50%', backgroundColor: '#e0e0e0', display: 'flex', alignItems: 'center', justifyContent: 'center', }}
              title="Cerrar chat"
            >
              <ChevronDown size={18} color="#444" />
            </button>            
          </div>

            {/* CONTENEDOR DE MENSAJES */}
            <div
              style={{
                position: 'relative',
                borderRadius: '8px',
                padding: '1rem',
                flex: 0.97,  
                height: '340px',
                overflowY: 'auto',
                marginBottom: '0.5rem',
                backgroundColor: '#fff',
                display: 'flex',
                flexDirection: 'column',
                boxShadow: 'inset 0 -10px 10px -10px rgba(0,0,0,0.08), inset 0 10px 10px -10px rgba(0,0,0,0.08)',
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
                        flexDirection: 'column', // ⬅️ importante: apilado vertical
                        alignItems: msg.role === 'assistant' ? 'flex-start' : 'flex-end',
                      }}
                    >
                      <MessageBubble
                        role={msg.role}
                        content={msg.content}
                        disableAnimation={shouldDisableAnimation}
                        animationDelay={`${index * 0.05}s`} // 👈 le pasas el delay como prop
                      />
  
                    {msg.imageUrl && (
                      <div style={{ marginTop: '0.5rem' }}>
                        <Zoom>
                          <img
                            src={msg.imageUrl}
                            alt="Imagen del bot"
                            style={{
                              width: '130px',
                              height: '130px',
                              borderRadius: '10px',
                              objectFit: 'cover',
                              cursor: 'pointer',
                              boxShadow: '0 2px 5px rgba(0,0,0,0.3)',
                            }}
                          />
                        </Zoom>
                      </div>
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
                marginLeft: '15px', 
                border: 'none',
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
                if (e.key === 'Enter' && !isTyping && inputValue.trim()) handleSendMessage();
              }}
              placeholder={currentLanguage.placeholder}
              disabled={false}
              readOnly={false}
            />
            {inputValue.trim() && (
              <div
              style={{
                transition: 'opacity 0.6s ease, transform 0.6s ease',
                opacity: inputValue.trim() ? 1 : 0,
                transform: inputValue.trim() ? 'translateY(0)' : 'translateY(15px)',
                pointerEvents: inputValue.trim() ? 'auto' : 'none',
              }}
            >
              <button
                style={{
                  backgroundColor: isMobile ? (isTyping ? '#aaa' : '#1c83f4') : 'white',
                  color: '#fff',
                  border: 'none',
                  borderRadius: '45%',
                  marginRight: '15px',
                  marginTop: '3px', 
                  width: '50px',
                  height: '35px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '1.2rem',
                  cursor: isTyping ? 'not-allowed' : 'pointer',
                  transition: 'background-color 0.3s ease',
                }}
                onClick={handleSendMessage}
                disabled={isTyping || !inputValue.trim()}
                title={currentLanguage.send} // tooltip al pasar el mouse
              >
                {isMobile ? <Send size={20} color="white" /> : (isTyping ? <Send size={20} color="#aaa" /> : <Send size={20} color="#1c83f4" />)}
              </button>
              </div>
              )}
            </div>
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
                <div style={{ position: 'relative' }}>
                  <button
                    onClick={closeModal}
                    style={{
                      position: 'absolute',
                      top: '-20px',
                      right: '-20px',
                      background: '#fff',
                      borderRadius: '50%',
                      border: 'none',
                      width: '30px',
                      height: '30px',
                      cursor: 'pointer',
                    }}
                  >
                    ✕
                  </button>
                  <img
                    src={selectedImage}
                    alt="Imagen ampliada"
                    style={{
                      maxWidth: '80vw',
                      maxHeight: '80vh',
                      borderRadius: '8px',
                      boxShadow: '0 2px 10px rgba(0,0,0,0.5)',
                      border: '1px solid #fff',
                    }}
                  />
                </div>
              </div>
            )}
            </div>   
      ) : (
        <button
          onClick={() => setIsChatOpen(true)}
          style={{
            position: 'fixed',
            bottom: '20px',
            right: '20px',
            width: '50px',
            height: '50px',
            borderRadius: '50%',
            backgroundColor: '#1c83f4',
            color: '#fff',
            border: 'none',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '1.5rem',
            cursor: 'pointer',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)',
            zIndex: 9999,
          }}
          title="Abrir chat"
        >
          <MessageCircle size={24} color="white" />
        </button>
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
          
    </>
  );
  
};

export default ChatBotUI;