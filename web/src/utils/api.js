/**
 * API клиент для работы с бэкендом
 */

const API_BASE_URL = "https://crispily-justicelike-maryjane.ngrok-free.dev";

/**
 * Получить статус календаря для пользователя
 */
export const getCalendarStatus = async (telegramId) => {
  const url = `${API_BASE_URL}/api/calendar/status/?telegram_id=${telegramId}`;
  console.log("API Request URL:", url);
  console.log("API Base URL:", API_BASE_URL);

  try {
    const response = await fetch(url, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    console.log("API Response status:", response.status);
    console.log("API Response ok:", response.ok);

    // Получаем текст ответа для проверки
    const responseText = await response.text();
    console.log("API Response text:", responseText);

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
    console.error("Error details:", {
      message: error.message,
      stack: error.stack,
    });
    throw error;
  }
};

/**
 * Открыть подарок за определенный день
 */
export const openGift = async (telegramId, day) => {
  const url = `${API_BASE_URL}/api/calendar/open/`;
  console.log("API Request URL (openGift):", url);

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
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
