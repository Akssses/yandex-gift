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

    if (!response.ok) {
      const errorText = await response.text();
      console.error("API Error response:", errorText);
      throw new Error(
        `HTTP error! status: ${response.status}, message: ${errorText}`
      );
    }

    const data = await response.json();
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
  try {
    const response = await fetch(`${API_BASE_URL}/api/calendar/open/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        telegram_id: telegramId,
        day: day,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.error || `HTTP error! status: ${response.status}`
      );
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error opening gift:", error);
    throw error;
  }
};
