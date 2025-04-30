// MessageBubble.jsx
import React from 'react';
import './MessageBubble.css'; // Importamos sus estilos

const MessageBubble = ({ role, content, disableAnimation, animationDelay }) => {
  return (
    <div className={`message-container ${role}`}>
      <div
        className="message-bubble"
        style={{
          animation: disableAnimation ? 'none' : 'fadeInSlideUp 0.3s ease forwards',
          animationDelay: disableAnimation ? '0s' : animationDelay, // 👈 aplicamos el delay
        }}
      >
        {content}
      </div>
    </div>
  );
};


export default MessageBubble;
