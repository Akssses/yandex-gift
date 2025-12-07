/**
 * Утилиты для работы с Telegram WebApp API
 */

export const getTelegramUser = () => {
  if (typeof window === "undefined") {
    return null;
  }

  // Проверяем, что мы в Telegram WebApp
  if (window.Telegram?.WebApp) {
    const webApp = window.Telegram.WebApp;
    webApp.ready();

    const user = webApp.initDataUnsafe?.user;
    if (user) {
      console.log("Telegram user found:", user.id);
      return {
        id: user.id,
        username: user.username,
        first_name: user.first_name,
        last_name: user.last_name,
      };
    } else {
      console.warn("Telegram WebApp found but user data is not available");
      console.log("initDataUnsafe:", webApp.initDataUnsafe);
    }
  } else {
    console.warn(
      "Telegram WebApp not found. window.Telegram:",
      window.Telegram
    );
  }

  return null;
};

export const getTelegramUserId = () => {
  const user = getTelegramUser();
  return user?.id || null;
};
