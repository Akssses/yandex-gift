pm2;
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

/**
 * Инициализировать Telegram WebApp и развернуть на полный экран
 */
export const initTelegramWebApp = () => {
  if (typeof window === "undefined") {
    return;
  }

  // Проверяем, что мы в Telegram WebApp
  if (window.Telegram?.WebApp) {
    const webApp = window.Telegram.WebApp;

    // Говорим Telegram, что приложение готово
    webApp.ready();

    // Разворачиваем на полный экран
    webApp.expand();

    // Настраиваем цвета (опционально)
    // webApp.setHeaderColor("#1a1a1a"); // Цвет заголовка
    // webApp.setBackgroundColor("#ffffff"); // Цвет фона

    // Отключаем кнопку "Назад" (опционально)
    // webApp.BackButton.hide();

    console.log("Telegram WebApp initialized and expanded to fullscreen");

    return webApp;
  } else {
    console.warn("Telegram WebApp not found");
  }

  return null;
};
