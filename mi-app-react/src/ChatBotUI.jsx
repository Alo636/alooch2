import React, {useState, useRef, useEffect} from 'react';
import { User2 } from 'lucide-react';

// Opcional: puedes añadir aquí otras banderas y nombres de idiomas que quieras soportar
const LANGUAGES = [
  {
    code: 'es',
    name: 'Español',
    flagUrl: 'https://cdn-icons-png.flaticon.com/512/197/197593.png', // Bandera de España
    placeholder: "Escribe tu mensaje...",
    send: "Enviar",
    reset: "Reiniciar conversación",
  },
  {
    code: 'en',
    name: 'English',
    flagUrl: 'https://cdn-icons-png.flaticon.com/512/197/197374.png', // Bandera (EE.UU./Inglaterra)
    placeholder: "Type your message...",
    send: "Send",
    reset: "Restart conversation",
  },
  {
    code: 'fr',
    name: 'Français',
    flagUrl: 'https://cdn-icons-png.flaticon.com/512/197/197560.png', // Bandera de Francia
    placeholder: "Écris ton message...",
    send: "Envoyer",
    reset: "Redémarrer la conversation",
  },
  {
    code: 'it',
    name: 'Italiano',
    flagUrl: 'https://cdn-icons-png.flaticon.com/512/197/197626.png', // Bandera de Italia
    placeholder: "Scrivi il tuo messaggio...",
    send: "Invia",
    reset: "Riavvia la conversazione",
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

  const [userId, setUserId] = useState(() => localStorage.getItem('userId') || null); 
  const [userData, setUserData] = useState(() => JSON.parse(localStorage.getItem('userData')) || null);

  // 🆕 Estados para autenticación
  const [authVisible, setAuthVisible] = useState(false);
  const [authMode, setAuthMode] = useState("login");
  const [authUsername, setAuthUsername] = useState("");
  const [authPassword, setAuthPassword] = useState("");
  const [authConfirmPassword, setAuthConfirmPassword] = useState("");
  const [authEmail, setAuthEmail] = useState("");
  const [authPhone, setAuthPhone] = useState("");

  // Función para encontrar el objeto de idioma actualmente seleccionado
  const currentLanguage = LANGUAGES.find((lang) => lang.code === language);

  const messagesEndRef = useRef(null);

  const [editandoPerfil, setEditandoPerfil] = useState(false);

  const [userHistory, setUserHistory] = useState([]);
  const [showingHistory, setShowingHistory] = useState(false);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  useEffect(() => {
    if (userId && userData) {
      setAuthVisible(true); // Mostrar el panel del usuario al iniciar si ya está autenticado
    }
  }, []);
  
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
          user_id: userId
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

  const handleLogout = () => {
    localStorage.removeItem('userId');
    localStorage.removeItem('userData');
    setUserId(null);
    setUserData(null);
    setMessages([]);
    setAuthVisible(false);
  };
  
  return (
    <div style={{ maxWidth: '600px', margin: '0 auto', marginTop: '2rem', backgroundColor: '#fff', borderRadius: '10px', boxShadow: '0 2px 10px rgba(0,0,0,0.2)', padding: '2rem', fontFamily: 'Georgia, serif', color: '#000' }}>
      <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
      <button
        onClick={() => {
          if (userId && userData) {
            setAuthVisible((prev) => !prev); // Mostrar/ocultar panel del usuario logueado
          } else {
            setAuthMode("login");
            setAuthVisible(true); // Mostrar formulario de login
          }
        }}
        style={{
          background: 'none',
          border: 'none',
          fontSize: '1.5rem',
          cursor: 'pointer',
          color: '#000',
        }}
        title={userId ? "Ver perfil" : "Iniciar sesión / Registrarse"}
      >
        <User2 style={{ color: userId ? "green" : "#000" }} />
      </button>

      </div>

      {authVisible && (
      <div
        style={{
          backgroundColor: '#fff',
          border: '1px solid #ccc',
          borderRadius: '10px',
          padding: '1.2rem',
          width: '100%',
          maxWidth: '320px',
          marginBottom: '1rem',
          boxShadow: '0 3px 8px rgba(0,0,0,0.15)',
          marginLeft: 'auto',
          color: '#000',
          fontFamily: 'inherit'
        }}
      >
        {userId && userData ? (
          <>
            <h2 style={{ marginTop: 0, marginBottom: '0.5rem' }}>Mi perfil</h2>
            <p><strong>Usuario:</strong> {userData.username}</p>
            <div style={{ marginBottom: '0.8rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <strong style={{ fontSize: '1rem' }}>Datos de contacto</strong>
              <button
                onClick={() => setEditandoPerfil((prev) => !prev)}
                title="Editar"
                style={{
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  fontSize: '1.2rem',
                  color: '#888',
                }}
              >
                ✏️
              </button>
            </div>

            {!editandoPerfil ? (
              <div style={{ marginTop: '0.5rem' }}>
                <p><strong>Email:</strong> {userData.email}</p>
                <p><strong>Teléfono:</strong> {userData.telefono || "No indicado"}</p>
              </div>
            ) : (
              <>
                <label style={{ display: 'block', marginBottom: '0.5rem' }}>
                  <strong>Email:</strong>
                  <input
                    type="email"
                    value={userData.email || ""}
                    onChange={(e) =>
                      setUserData((prev) => ({ ...prev, email: e.target.value }))
                    }
                    style={{
                      width: '100%',
                      marginTop: '0.2rem',
                      padding: '0.4rem',
                      borderRadius: '4px',
                      border: '1px solid #ccc',
                    }}
                  />
                </label>

                <label style={{ display: 'block', marginBottom: '0.5rem' }}>
                  <strong>Teléfono:</strong>
                  <input
                    type="tel"
                    value={userData.telefono || ""}
                    onChange={(e) =>
                      setUserData((prev) => ({ ...prev, telefono: e.target.value }))
                    }
                    style={{
                      width: '100%',
                      marginTop: '0.2rem',
                      padding: '0.4rem',
                      borderRadius: '4px',
                      border: '1px solid #ccc',
                    }}
                  />
                </label>
                <button
                  onClick={async () => {
                    try {
                      const res = await fetch("http://127.0.0.1:8000/update_user", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                          user_id: userId,
                          email: userData.email,
                          telefono: userData.telefono ? userData.telefono : null,
                        }),
                      });
                    
                      const result = await res.json();
                    
                      if (!res.ok) {
                        console.error("❌ Error al actualizar perfil:", result);
                        alert("❌ Error al actualizar perfil:\n" + JSON.stringify(result, null, 2));
                        return;
                      }
                    
                      localStorage.setItem("userData", JSON.stringify(userData));
                      alert("✅ Perfil actualizado correctamente");
                      setEditandoPerfil(false);
                    } catch (err) {
                      console.error("❌ Error al conectar:", err);
                      alert("❌ Error al conectar con el servidor");
                    }
                    
                  }}
                  style={{
                    backgroundColor: '#007bff',
                    color: '#fff',
                    border: 'none',
                    borderRadius: '5px',
                    padding: '0.5rem',
                    width: '100%',
                    marginBottom: '1rem',
                    cursor: 'pointer',
                  }}
                >
                  💾 Guardar cambios
                </button>
              </>
            )}
          </div>

            <hr style={{ margin: '1rem 0' }} />

            <button
              onClick={async () => {
                try {
                  const res = await fetch(`http://127.0.0.1:8000/user_history/${userId}`);
                  const data = await res.json();
                  if (!res.ok) throw new Error(data.detail || "Error obteniendo historial");
                  setUserHistory(data.historial);
                  setShowingHistory(true);
                } catch (err) {
                  alert("❌ Error al cargar el historial: " + err.message);
                }
              }}

              style={{
                width: '100%',
                marginBottom: '0.5rem',
                backgroundColor: '#f5f5f5',
                border: '1px solid #ccc',
                borderRadius: '5px',
                padding: '0.5rem',
                cursor: 'pointer',
              }}
            >
              🕒 Ver historial
            </button>

            <button
              onClick={() => alert("Configuración no implementada aún")}
              style={{
                width: '100%',
                marginBottom: '0.5rem',
                backgroundColor: '#f5f5f5',
                border: '1px solid #ccc',
                borderRadius: '5px',
                padding: '0.5rem',
                cursor: 'pointer',
              }}
            >
              ⚙️ Configuración
            </button>

            <button
              onClick={() => alert("Política de privacidad no implementada aún")}
              style={{
                width: '100%',
                marginBottom: '0.5rem',
                backgroundColor: '#f5f5f5',
                border: '1px solid #ccc',
                borderRadius: '5px',
                padding: '0.5rem',
                cursor: 'pointer',
              }}
            >
              📄 Política de privacidad
            </button>
            <button
              onClick={handleLogout}
              style={{
                backgroundColor: '#000',
                color: '#fff',
                border: 'none',
                borderRadius: '5px',
                padding: '0.5rem',
                width: '100%',
                cursor: 'pointer',
                fontWeight: 'bold',
                marginTop: '0.5rem',
              }}
            >
              🔐 Cerrar sesión
            </button>
            {showingHistory && (
              <div
                style={{
                  backgroundColor: "#f9f9f9",
                  border: "1px solid #ccc",
                  borderRadius: "10px",
                  padding: "1rem",
                  maxHeight: "300px",
                  overflowY: "scroll",
                  marginBottom: "1rem",
                  color: "#000",
                  fontFamily: "inherit",
                  textAlign: "left",
                }}
              >
                <h3>🕒 Historial de conversaciones</h3>
                <button
                  onClick={() => setShowingHistory(false)}
                  style={{
                    marginBottom: "0.8rem",
                    backgroundColor: "#ddd",
                    border: "none",
                    padding: "0.4rem 0.6rem",
                    borderRadius: "5px",
                    cursor: "pointer",
                    color: "#000"
                  }}
                >
                  Cerrar
                </button>
                {userHistory.length === 0 ? (
                  <p>No hay conversaciones anteriores.</p>
                ) : (
                  Object.entries(
                    userHistory.reduce((acc, conv) => {
                      const fecha = new Date(conv.created_at);
                      const dateKey = fecha.toLocaleDateString();
                      const minuteKey = fecha.getHours().toString().padStart(2, '0') + ':' + fecha.getMinutes().toString().padStart(2, '0');
                      if (!acc[dateKey]) acc[dateKey] = {};

                      // Si ya hay una conversación en el mismo minuto, comparar por created_at
                      if (!acc[dateKey][minuteKey] || new Date(conv.created_at) > new Date(acc[dateKey][minuteKey].created_at)) {
                        acc[dateKey][minuteKey] = conv;
                      }
                      return acc;
                    }, {})
                  ).sort((a, b) => new Date(b[0]) - new Date(a[0]))
                    .map(([date, convsByMinute]) => {
                      const conversaciones = Object.values(convsByMinute).sort(
                        (a, b) => new Date(a.created_at) - new Date(b.created_at)
                      );
                      return (
                        <div key={date} style={{ marginBottom: "1.5rem" }}>
                          <h4 style={{ color: "#333", marginBottom: "0.5rem" }}>{date}</h4>
                          <div style={{ fontSize: "0.95rem", whiteSpace: "pre-wrap" }}>
                            {conversaciones.flatMap((conv, i) =>
                              conv.contenido.map((msg, j) => (
                                <p key={`${i}-${j}`} style={{ marginLeft: "1rem" }}>
                                  <span style={{ color: "#666", marginRight: "0.4rem" }}>
                                    {new Date(conv.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                  </span>
                                  <strong>{msg.role === "user" ? "🧍 Usuario" : "🤖 Asistente"}:</strong> {msg.content}
                                </p>
                              ))
                            )}
                          </div>
                        </div>
                      );
                    })
                )}
              </div>
            )}
          </>
          ) : (
            <>
              <input type="text" placeholder="Nombre de usuario" value={authUsername} onChange={(e) => setAuthUsername(e.target.value)} style={{ width: '100%', padding: '0.5rem', marginBottom: '0.5rem', borderRadius: '4px', border: '1px solid #ccc', fontSize: '0.95rem', fontFamily: 'inherit', color: '#000' }} />
              <input type="password" placeholder="Contraseña" value={authPassword} onChange={(e) => setAuthPassword(e.target.value)} style={{ width: '100%', padding: '0.5rem', marginBottom: '0.5rem', borderRadius: '4px', border: '1px solid #ccc', fontSize: '0.95rem', fontFamily: 'inherit', color: '#000' }} />
              {authMode === "register" && (
                <>
                  <input type="password" placeholder="Confirmar contraseña" value={authConfirmPassword} onChange={(e) => setAuthConfirmPassword(e.target.value)} style={{ width: '100%', padding: '0.5rem', marginBottom: '0.5rem', borderRadius: '4px', border: '1px solid #ccc', fontSize: '0.95rem', fontFamily: 'inherit', color: '#000' }} />
                  <input type="email" placeholder="Email" value={authEmail} onChange={(e) => setAuthEmail(e.target.value)} style={{ width: '100%', padding: '0.5rem', marginBottom: '0.5rem', borderRadius: '4px', border: '1px solid #ccc', fontSize: '0.95rem', fontFamily: 'inherit', color: '#000' }} />
                  <input type="tel" placeholder="Teléfono (opcional)" value={authPhone} onChange={(e) => setAuthPhone(e.target.value)} style={{ width: '100%', padding: '0.5rem', marginBottom: '0.5rem', borderRadius: '4px', border: '1px solid #ccc', fontSize: '0.95rem', fontFamily: 'inherit', color: '#000' }} />
                </>
              )}
              <button onClick={async () => {
                if (!authUsername || !authPassword) return alert("Usuario y contraseña son obligatorios");
                if (authMode === "register") {
                  if (!authEmail) return alert("El email es obligatorio");
                  if (authPassword !== authConfirmPassword) return alert("Las contraseñas no coinciden");
                }
                try {
                  const body = authMode === "register"
                    ? { username: authUsername, password: authPassword, email: authEmail, ...(authPhone && { telefono: authPhone }) }
                    : { username: authUsername, password: authPassword };
                  const res = await fetch(`http://127.0.0.1:8000/${authMode}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(body),
                  });
                  const data = await res.json();
                  if (!res.ok) return alert(data.detail || "Error de autenticación");
                  localStorage.setItem("userId", data.user_id);
                  localStorage.setItem("userData", JSON.stringify(data));
                  setUserId(data.user_id);
                  setUserData(data);
                  setAuthVisible(false);
                  setAuthUsername("");
                  setAuthPassword("");
                  setAuthConfirmPassword("");
                  setAuthEmail("");
                  setAuthPhone("");
                  alert("Autenticación correcta");
                } catch (err) {
                  console.error(err);
                  alert("Error al conectar");
                }
              }} style={{ backgroundColor: '#000', color: '#fff', border: 'none', borderRadius: '5px', padding: '0.5rem', width: '100%', marginBottom: '0.5rem', cursor: 'pointer', fontWeight: 'bold' }}>
                {authMode === "login" ? "Iniciar sesión" : "Registrarse"}
              </button>
              <div style={{ fontSize: '0.9rem' }}>
                {authMode === "login"
                  ? <>¿No tienes cuenta? <button onClick={() => setAuthMode("register")} style={{ background: 'none', border: 'none', color: '#007bff', cursor: 'pointer', textDecoration: 'underline', padding: 0 }}>Regístrate</button></>
                  : <>¿Ya tienes cuenta? <button onClick={() => setAuthMode("login")} style={{ background: 'none', border: 'none', color: '#007bff', cursor: 'pointer', textDecoration: 'underline', padding: 0 }}>Inicia sesión</button></>
                }
              </div>
            </>
          )}
        </div>
      )}
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
                  backgroundColor: msg.role === 'assistant' ? '#f8f8f8' : '#000',
                  color: msg.role === 'assistant' ? '#000' : '#fff',
                  padding: '0.6rem 1rem',
                  borderRadius: '15px',
                  maxWidth: '70%',
                  minHeight: '35px',
                  display: 'flex',
                  alignItems: 'center',
                  whiteSpace: 'pre-wrap',
                  boxShadow: '0 1px 3px rgba(0,0,0,0.2)',
                  border: msg.role === 'assistant' ? '1px solid #ccc' : '1px solid #000',
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
        <div ref={messagesEndRef} />
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
          placeholder={currentLanguage.placeholder}
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
          {currentLanguage.send}
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