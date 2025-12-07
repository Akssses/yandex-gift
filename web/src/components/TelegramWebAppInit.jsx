"use client";

import { useEffect } from "react";
import { initTelegramWebApp } from "@/utils/telegram";

/**
 * Компонент для инициализации Telegram WebApp
 * Разворачивает приложение на полный экран при загрузке
 */
export default function TelegramWebAppInit() {
  useEffect(() => {
    // Ждем загрузки скрипта Telegram WebApp
    const initWebApp = () => {
      // Пытаемся инициализировать сразу
      let webApp = initTelegramWebApp();

      // Если WebApp еще не загружен, ждем
      if (!webApp) {
        let attempts = 0;
        const maxAttempts = 20; // 2 секунды максимум

        const interval = setInterval(() => {
          attempts++;
          webApp = initTelegramWebApp();

          if (webApp || attempts >= maxAttempts) {
            clearInterval(interval);
          }
        }, 100);
      }
    };

    // Запускаем инициализацию после небольшой задержки
    // чтобы скрипт Telegram точно загрузился
    const timeout = setTimeout(initWebApp, 100);

    return () => {
      clearTimeout(timeout);
    };
  }, []);

  return null; // Компонент не рендерит ничего
}
