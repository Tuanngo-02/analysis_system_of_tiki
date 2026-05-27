import { useEffect, useMemo, useRef, useState } from "react";
import { apiService } from "../services/api";
import "../styles/ChatWidget.css";

const initialMessage = {
  id: "bot-welcome",
  role: "bot",
  text:
    "Chào bạn. Mình có thể tư vấn điện thoại, máy tính bảng, sách và phụ kiện máy tính. Bạn muốn mua sản phẩm gì?",
};

const quickPrompts = [
  "Tôi muốn mua điện thoại",
  "Tôi muốn mua chuột không dây",
  "Tôi muốn mua sách",
];

function ProductCards({ products = [] }) {
  if (!products.length) return null;

  return (
    <div className="chat-products">
      {products.map((product, index) => (
        <article key={`${product.product_id || product.product_url || index}`} className="chat-product-card">
          <div className="chat-product-image">
            {product.thumbnail_url ? (
              <img src={product.thumbnail_url} alt={product.name} loading="lazy" />
            ) : (
              <span>{index + 1}</span>
            )}
          </div>
          <div className="chat-product-info">
            <div className="chat-product-rank">#{index + 1}</div>
            <h3>{product.name}</h3>
            {product.brand && <p className="chat-product-brand">{product.brand}</p>}
            <div className="chat-product-meta">
              <strong>{product.price_text || "Chưa rõ giá"}</strong>
              <span>
                {product.rating_average ?? "N/A"}/5 · {product.review_count || 0} đánh giá
              </span>
            </div>
            {product.product_url && (
              <a href={product.product_url} target="_blank" rel="noopener noreferrer">
                Xem trên Tiki
              </a>
            )}
          </div>
        </article>
      ))}
    </div>
  );
}

function LinkifiedText({ text }) {
  const parts = String(text || "").split(/(https?:\/\/[^\s]+)/g);
  return parts.map((part, index) =>
    /^https?:\/\//.test(part) ? (
      <a key={`${part}-${index}`} href={part} target="_blank" rel="noopener noreferrer">
        {part}
      </a>
    ) : (
      <span key={`${part}-${index}`}>{part}</span>
    )
  );
}

export function ChatWidget({ user }) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([initialMessage]);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [conversationId, setConversationId] = useState(() => Date.now());
  const messagesEndRef = useRef(null);

  const senderId = useMemo(() => {
    const userPart = user?.username || user?.email || "guest";
    return `frontend-${userPart}-${conversationId}`;
  }, [conversationId, user]);

  useEffect(() => {
    if (isOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
    }
  }, [isOpen, messages]);

  const appendMessage = (message) => {
    setMessages((current) => [
      ...current,
      {
        id: `${message.role}-${Date.now()}-${Math.random().toString(16).slice(2)}`,
        ...message,
      },
    ]);
  };

  const sendMessage = async (text) => {
    const trimmed = text.trim();
    if (!trimmed || isSending) return;

    appendMessage({ role: "user", text: trimmed });
    setInput("");
    setIsSending(true);

    try {
      const botResponses = await apiService.sendChatMessage(trimmed, senderId);
      const responseText =
        botResponses
          ?.map((item) => item.text)
          .filter(Boolean)
          .join("\n\n") ||
        "Mình chưa nhận được phản hồi từ chatbot. Bạn thử lại nhé.";
      const products = botResponses?.flatMap((item) => item.custom?.products || []) || [];
      const category = botResponses?.find((item) => item.custom?.category)?.custom?.category || "";

      appendMessage({ role: "bot", text: responseText, products, category });
    } catch {
      appendMessage({
        role: "bot",
        text:
          "Không kết nối được chatbot. Kiểm tra Rasa server tại http://localhost:5005 và action server.",
      });
    } finally {
      setIsSending(false);
    }
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    sendMessage(input);
  };

  const resetChat = () => {
    setMessages([initialMessage]);
    setInput("");
    setConversationId(Date.now());
  };

  return (
    <div className="chat-widget" aria-live="polite">
      {isOpen && (
        <section className="chat-panel" aria-label="Hộp thoại chatbot tư vấn">
          <header className="chat-header">
            <div>
              <h2>Tư vấn Tiki</h2>
              <span>Rasa chatbot</span>
            </div>
            <div className="chat-header-actions">
              <button type="button" className="chat-icon-btn" onClick={resetChat} title="Làm mới">
                ↻
              </button>
              <button
                type="button"
                className="chat-icon-btn"
                onClick={() => setIsOpen(false)}
                title="Thu nhỏ"
              >
                ×
              </button>
            </div>
          </header>

          <div className="chat-messages">
            {messages.map((message) => (
              <div key={message.id} className={`chat-message ${message.role}`}>
                <div className={`chat-bubble ${message.products?.length ? "has-products" : ""}`}>
                  {message.products?.length ? (
                    <>
                      <div className="chat-products-title">
                        <strong>Top {message.products.length} sản phẩm phù hợp</strong>
                        {message.category && <span>{message.category}</span>}
                      </div>
                      <ProductCards products={message.products} />
                    </>
                  ) : (
                    <LinkifiedText text={message.text} />
                  )}
                </div>
              </div>
            ))}
            {isSending && (
              <div className="chat-message bot">
                <div className="chat-bubble typing">Đang trả lời...</div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {messages.length === 1 && (
            <div className="chat-suggestions">
              {quickPrompts.map((prompt) => (
                <button key={prompt} type="button" onClick={() => sendMessage(prompt)}>
                  {prompt}
                </button>
              ))}
            </div>
          )}

          <form className="chat-input-row" onSubmit={handleSubmit}>
            <input
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="Nhập nhu cầu mua hàng..."
              disabled={isSending}
            />
            <button type="submit" disabled={isSending || !input.trim()} title="Gửi">
              ➤
            </button>
          </form>
        </section>
      )}

      <button
        type="button"
        className="chat-toggle"
        onClick={() => setIsOpen((current) => !current)}
        aria-label={isOpen ? "Đóng chatbot" : "Mở chatbot"}
      >
        {isOpen ? "×" : "💬"}
      </button>
    </div>
  );
}
