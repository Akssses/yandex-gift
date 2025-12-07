/**
 * API клиент для работы с бэкендом
 */

// API Base URL - можно переопределить через переменную окружения
// Установите NEXT_PUBLIC_API_URL в .env.local для указания URL бэкенда
// В production используем проксирование через Next.js, в development - прямой URL
const getApiBaseUrl = () => {
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }

  // Если мы на Vercel (production), используем проксирование через Next.js
  // Это необходимо для обхода Mixed Content (HTTPS -> HTTP)
  if (
    typeof window !== "undefined" &&
    window.location.hostname.includes("vercel.app")
  ) {
    return ""; // Относительный путь - будет проксироваться через Next.js
  }

  // В development используем прямой URL (HTTPS)
  return "https://advent.muza.team";
};

const API_BASE_URL = getApiBaseUrl();

console.log("API_BASE_URL configured as:", API_BASE_URL);
console.log("NEXT_PUBLIC_API_URL from env:", process.env.NEXT_PUBLIC_API_URL);

/**
 * Проверить доступность сервера
 */
export const checkServerHealth = async () => {
  const baseUrl = API_BASE_URL || "";
  const url = `${baseUrl}/api/health`; // Без trailing slash (APPEND_SLASH = False)
  console.log("Health check URL:", url);

  try {
    const response = await fetch(url, {
      method: "GET",
      mode: "cors",
      cache: "no-cache",
      credentials: "omit",
      headers: {
        Accept: "application/json",
      },
    });

    console.log("Health check response status:", response.status);
    console.log("Health check response ok:", response.ok);
    console.log("Health check response headers:", [
      ...response.headers.entries(),
    ]);

    if (!response.ok) {
      const text = await response.text();
      console.error(
        "Health check failed with status:",
        response.status,
        "Response:",
        text
      );
      return false;
    }

    const data = await response.json();
    console.log("Health check data:", data);
    return data.status === "ok";
  } catch (error) {
    console.error("Server health check failed:", error);
    console.error("Error type:", error?.constructor?.name);
    console.error("Error message:", error?.message);
    console.error("Error stack:", error?.stack);
    return false;
  }
};

/**
 * Проверить, есть ли пользователь в базе данных
 */
export const checkUser = async (telegramId) => {
  if (!telegramId) {
    throw new Error("telegram_id is required");
  }

  const baseUrl = API_BASE_URL || "";
  const url = `${baseUrl}/api/check-user?id=${telegramId}`; // Без trailing slash
  console.log("Checking user URL:", url);

  try {
    const response = await fetch(url, {
      method: "GET",
      mode: "cors",
      cache: "no-cache",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
    });

    console.log("Check user response status:", response.status);

    const responseText = await response.text();
    console.log("Check user response text:", responseText);

    if (!response.ok) {
      let errorMessage = responseText;
      try {
        const errorData = JSON.parse(responseText);
        errorMessage = errorData.error || errorData.message || responseText;
      } catch (e) {}

      throw new Error(
        `HTTP error! status: ${response.status}, message: ${errorMessage}`
      );
    }

    let data;
    try {
      data = JSON.parse(responseText);
    } catch (e) {
      console.error("Failed to parse JSON:", e);
      throw new Error(
        `Invalid JSON response: ${responseText.substring(0, 100)}`
      );
    }

    console.log("Check user response data:", data);
    return data;
  } catch (error) {
    console.error("Error checking user:", error);
    throw error;
  }
};

/**
 * Получить статус календаря для пользователя
 */
export const getCalendarStatus = async (telegramId) => {
  if (!telegramId) {
    throw new Error("telegram_id is required");
  }

  // Используем относительный путь если API_BASE_URL пустой (проксирование)
  const baseUrl = API_BASE_URL || "";
  const url = `${baseUrl}/api/calendar/status?telegram_id=${telegramId}`; // Без trailing slash
  console.log("API Request URL:", url);
  console.log("API Base URL:", API_BASE_URL);
  console.log("Telegram ID:", telegramId);

  try {
    // Проверяем доступность сервера перед запросом
    console.log("Attempting to fetch from:", url);
    console.log("Current origin:", window.location.origin);

    const response = await fetch(url, {
      method: "GET",
      mode: "cors", // Явно указываем режим CORS
      cache: "no-cache", // Не кэшируем запросы
      credentials: "omit", // Не отправляем cookies
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
    });

    console.log("Response received:", {
      status: response.status,
      ok: response.ok,
      headers: Object.fromEntries(response.headers.entries()),
    });

    console.log("API Response status:", response.status);
    console.log("API Response ok:", response.ok);
    console.log(
      "API Response headers:",
      Object.fromEntries(response.headers.entries())
    );

    // Получаем текст ответа для проверки
    const responseText = await response.text();
    console.log("API Response text length:", responseText.length);
    console.log("API Response text preview:", responseText.substring(0, 200));

    if (!response.ok) {
      console.error("API Error response:", responseText);
      // Пытаемся распарсить как JSON, если не получается - используем текст
      let errorMessage = responseText;
      try {
        const errorData = JSON.parse(responseText);
        errorMessage = errorData.error || errorData.message || responseText;
      } catch (e) {
        // Если не JSON, используем текст как есть
      }
      throw new Error(
        `HTTP error! status: ${response.status}, message: ${errorMessage}`
      );
    }

    // Пытаемся распарсить JSON
    let data;
    try {
      data = JSON.parse(responseText);
    } catch (e) {
      console.error("Failed to parse JSON:", e);
      console.error("Response text:", responseText);
      throw new Error(
        `Invalid JSON response: ${responseText.substring(0, 100)}`
      );
    }

    console.log("API Response data:", data);
    return data;
  } catch (error) {
    console.error("Error fetching calendar status:", error);
    console.error("Error type:", error?.constructor?.name);
    console.error("Error message:", error?.message);
    console.error("Error stack:", error?.stack);
    console.error("Full error object:", error);
    console.error("API URL that failed:", url);

    // Определяем тип ошибки
    let errorMessage = error?.message || "Unknown error occurred";

    // Если это сетевая ошибка
    if (
      error?.message?.includes("Failed to fetch") ||
      error?.message?.includes("Load failed") ||
      error?.message?.includes("NetworkError") ||
      error?.name === "TypeError" ||
      error?.message?.includes("Network request failed") ||
      error?.message?.includes("Mixed Content")
    ) {
      // Проверяем, может быть это Mixed Content ошибка (HTTPS -> HTTP)
      const isMixedContent =
        typeof window !== "undefined" &&
        window.location.protocol === "https:" &&
        API_BASE_URL.startsWith("http://");

      if (isMixedContent) {
        errorMessage = `Ошибка Mixed Content: HTTPS сайт не может обращаться к HTTP серверу. 
        
Решение:
1. Настройте HTTPS для бэкенда (advent.muza.team)
2. Или используйте проксирование через Vercel
3. Текущий API URL: ${API_BASE_URL}`;
      } else {
        // Проверяем, может быть это CORS ошибка
        const isCorsError =
          error?.message?.includes("CORS") ||
          error?.message?.includes("cross-origin") ||
          error?.message?.includes("Access-Control");

        if (isCorsError) {
          errorMessage = `Ошибка CORS: Запрос заблокирован из-за политики CORS. 
          
Проверьте:
1. Что бэкенд настроен на разрешение запросов с вашего домена
2. Что CORS middleware правильно настроен
3. Текущий origin: ${
            typeof window !== "undefined" ? window.location.origin : "unknown"
          }`;
        } else {
          errorMessage = `Не удалось подключиться к серверу. 
          
Возможные причины:
1. Бэкенд не запущен - проверьте, что Django сервер работает
2. Неправильный URL бэкенда - текущий URL: ${API_BASE_URL}
3. Проблема с сетью - проверьте интернет соединение
4. Mixed Content - HTTPS сайт не может обращаться к HTTP

Попробуйте открыть в браузере: ${API_BASE_URL}/api/health/`;
        }
      }
    }

    // Создаем более информативную ошибку
    const enhancedError = new Error(
      `Failed to fetch calendar status: ${errorMessage}`
    );
    enhancedError.originalError = error;
    enhancedError.url = url;
    throw enhancedError;
  }
};

/**
 * Открыть подарок за определенный день
 */
export const openGift = async (telegramId, day) => {
  const baseUrl = API_BASE_URL || "";
  const url = `${baseUrl}/api/calendar/open`; // Без trailing slash (APPEND_SLASH = False)
  console.log("API Request URL (openGift):", url);

  try {
    const response = await fetch(url, {
      method: "POST",
      mode: "cors", // Явно указываем режим CORS
      headers: {
        "Content-Type": "application/json",
        "ngrok-skip-browser-warning": "true", // Пропускаем предупреждение ngrok
      },
      body: JSON.stringify({
        telegram_id: telegramId,
        day: day,
      }),
    });

    console.log("API Response status (openGift):", response.status);
    console.log("API Response ok (openGift):", response.ok);

    // Получаем текст ответа для проверки
    const responseText = await response.text();
    console.log("API Response text (openGift):", responseText);

    if (!response.ok) {
      console.error("API Error response (openGift):", responseText);
      // Пытаемся распарсить как JSON, если не получается - используем текст
      let errorMessage = responseText;
      try {
        const errorData = JSON.parse(responseText);
        errorMessage = errorData.error || errorData.message || responseText;
      } catch (e) {
        // Если не JSON, используем текст как есть
      }
      throw new Error(
        `HTTP error! status: ${response.status}, message: ${errorMessage}`
      );
    }

    // Пытаемся распарсить JSON
    let data;
    try {
      data = JSON.parse(responseText);
    } catch (e) {
      console.error("Failed to parse JSON (openGift):", e);
      console.error("Response text:", responseText);
      throw new Error(
        `Invalid JSON response: ${responseText.substring(0, 100)}`
      );
    }

    console.log("API Response data (openGift):", data);
    return data;
  } catch (error) {
    console.error("Error opening gift:", error);
    throw error;
  }
};
