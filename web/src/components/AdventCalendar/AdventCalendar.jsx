"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import styles from "./AdventCalendar.module.scss";
import { getTelegramUserId } from "@/utils/telegram";
import {
  getCalendarStatus,
  openGift,
  checkServerHealth,
  checkUser,
} from "@/utils/api";

const AdventCalendar = () => {
  const [currentDay, setCurrentDay] = useState(0);
  const [days, setDays] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [accessDenied, setAccessDenied] = useState(false); // Доступ запрещен
  const [serverCurrentDay, setServerCurrentDay] = useState(null); // Текущий день с сервера
  const [telegramId, setTelegramId] = useState(null); // Сохраняем telegram_id в state
  const router = useRouter();

  // Проверяем доступ пользователя и загружаем статус календаря
  useEffect(() => {
    const loadCalendarStatus = async () => {
      try {
        setLoading(true);
        setAccessDenied(false);

        // Ждем инициализации Telegram WebApp
        let telegramId = getTelegramUserId();
        let attempts = 0;
        const maxAttempts = 10;

        // Пытаемся получить telegram_id с задержкой (на случай если скрипт еще не загрузился)
        while (!telegramId && attempts < maxAttempts) {
          await new Promise((resolve) => setTimeout(resolve, 100));
          telegramId = getTelegramUserId();
          attempts++;
        }

        console.log("Telegram ID:", telegramId);
        console.log("Attempts:", attempts);

        if (!telegramId) {
          // Если нет telegram_id, пробуем использовать тестовый ID из localStorage для разработки
          const testTelegramId = localStorage.getItem("test_telegram_id");
          if (testTelegramId) {
            console.log(
              "Using test telegram_id from localStorage:",
              testTelegramId
            );
            telegramId = parseInt(testTelegramId, 10);
          } else {
            // Если нет telegram_id, показываем ошибку доступа
            console.warn("Telegram user ID not found");
            setAccessDenied(true);
            setLoading(false);
            return;
          }
        }

        // Сохраняем telegram_id в state для использования при открытии подарка
        setTelegramId(telegramId);

        // Проверяем, есть ли пользователь в базе данных
        console.log("Checking user access for telegram_id:", telegramId);
        const userCheck = await checkUser(telegramId);

        if (!userCheck.exists) {
          // Пользователь не найден в базе
          console.warn("User not found in database");
          setAccessDenied(true);
          setLoading(false);
          return;
        }

        console.log("User found in database, loading calendar...");

        // Сначала проверяем доступность сервера
        console.log("Checking server health...");
        try {
          const isServerHealthy = await checkServerHealth();
          if (!isServerHealthy) {
            console.warn(
              "Health check returned false, but continuing anyway..."
            );
            // Не бросаем ошибку, продолжаем попытку запроса календаря
            // Возможно, health check не работает из-за CORS, но основной запрос может пройти
          } else {
            console.log("Server is healthy, fetching calendar status...");
          }
        } catch (healthError) {
          console.warn(
            "Health check failed, but continuing with calendar request:",
            healthError
          );
          // Продолжаем попытку запроса календаря
        }

        console.log(
          "Fetching calendar status from API for telegram_id:",
          telegramId
        );
        const data = await getCalendarStatus(telegramId);

        console.log("Calendar status from API:", data);
        console.log("Current day from API:", data.current_day);
        console.log("Days from API:", data.days);

        // Сохраняем текущий день с сервера
        setServerCurrentDay(data.current_day);

        // Преобразуем данные из API в формат компонента
        const formattedDays = data.days.map((dayData) => {
          const dayNumber = dayData.day;
          const dayString = String(dayNumber).padStart(2, "0");

          console.log(
            `Day ${dayNumber}: status=${dayData.status}, is_opened=${dayData.is_opened}`
          );

          return {
            day: dayString,
            dayNumber: dayNumber, // Сохраняем числовое значение для проверок
            month: "декабря",
            status: dayData.status,
            isOpened: dayData.is_opened,
            giftImage: dayData.is_opened
              ? "/assets/images/gift.png"
              : "/assets/images/gift2.png",
          };
        });

        console.log("Formatted days:", formattedDays);
        setDays(formattedDays);
        setError(null);
      } catch (err) {
        console.error("Failed to load calendar status:", err);
        console.error("Error type:", err?.constructor?.name);
        console.error("Error message:", err?.message);
        console.error("Error stack:", err?.stack);
        console.error("Full error:", err);

        const errorMessage = err?.message || "Неизвестная ошибка";
        setError(
          `Не удалось загрузить календарь: ${errorMessage}. Проверьте подключение к серверу.`
        );
        // НЕ используем моковые данные при ошибке - показываем ошибку
        setDays([]);
      } finally {
        setLoading(false);
      }
    };

    loadCalendarStatus();
  }, []);

  const handleNext = () => {
    setCurrentDay((prev) => (prev + 1) % days.length);
  };

  const handlePrev = () => {
    setCurrentDay((prev) => (prev - 1 + days.length) % days.length);
  };

  const currentDayData = days[currentDay] || {};

  const handleOpenGiftClick = async () => {
    console.log("handleOpenGiftClick called");
    console.log("currentDayData:", currentDayData);

    if (
      !currentDayData ||
      currentDayData.status === "locked" ||
      currentDayData.status === "missed"
    ) {
      console.log("Blocked: locked or missed status");
      return;
    }

    // Используем сохраненный telegram_id из state, если нет - пытаемся получить заново
    let currentTelegramId = telegramId || getTelegramUserId();

    // Если все еще нет, проверяем localStorage
    if (!currentTelegramId) {
      const testTelegramId = localStorage.getItem("test_telegram_id");
      if (testTelegramId) {
        currentTelegramId = parseInt(testTelegramId, 10);
      }
    }

    const dayNumber =
      currentDayData.dayNumber || parseInt(currentDayData.day, 10);

    console.log("Day number:", dayNumber);
    console.log("Status:", currentDayData.status);
    console.log("Server current day:", serverCurrentDay);
    console.log("Telegram ID from state:", telegramId);
    console.log("Telegram ID current:", currentTelegramId);

    // Если подарок уже открыт, просто переходим на страницу
    if (currentDayData.status === "opened") {
      console.log("Gift already opened, navigating to page");
      router.push(`/gift/${dayNumber}`);
      return;
    }

    // Если подарок доступен, открываем его
    if (currentDayData.status === "available") {
      console.log("Gift is available, attempting to open");

      // Проверяем, что это текущий день с сервера (можно открыть только текущий день)
      if (serverCurrentDay !== null && dayNumber !== serverCurrentDay) {
        console.log("Blocked: not current day", {
          dayNumber,
          serverCurrentDay,
        });
        alert(
          `Вы можете открыть подарок только за ${serverCurrentDay} декабря. Этот день недоступен.`
        );
        return;
      }

      // Если есть telegram_id, открываем через API
      if (currentTelegramId) {
        try {
          console.log("Opening gift via API", {
            telegramId: currentTelegramId,
            dayNumber,
          });
          await openGift(currentTelegramId, dayNumber);

          // Обновляем статус локально
          const updatedDays = [...days];
          updatedDays[currentDay] = {
            ...updatedDays[currentDay],
            status: "opened",
            isOpened: true,
            giftImage: "/assets/images/gift.png",
          };
          setDays(updatedDays);

          // Переходим на страницу подарка
          console.log("Gift opened successfully, navigating");
          router.push(`/gift/${dayNumber}`);
        } catch (error) {
          console.error("Failed to open gift:", error);
          const errorMessage = error.message || "Не удалось открыть подарок";

          // Показываем понятное сообщение об ошибке
          if (
            errorMessage.includes("missed") ||
            errorMessage.includes("пропущен")
          ) {
            alert("Этот день был пропущен. Подарок недоступен.");
          } else if (
            errorMessage.includes("not available") ||
            errorMessage.includes("недоступен")
          ) {
            alert("Этот день еще недоступен.");
          } else if (
            errorMessage.includes("current day") ||
            errorMessage.includes("текущий день")
          ) {
            alert(
              `Вы можете открыть подарок только за ${serverCurrentDay} декабря.`
            );
          } else {
            alert(errorMessage);
          }
        }
      } else {
        // Если нет telegram_id, просто переходим на страницу (для разработки)
        console.log("No telegram_id, navigating directly (dev mode)", {
          currentTelegramId,
        });
        router.push(`/gift/${dayNumber}`);
      }
    } else {
      // Если статус не available, не позволяем открывать
      console.log("Blocked: status is not available", currentDayData.status);
      alert("Этот подарок недоступен для открытия.");
    }
  };

  if (loading) {
    return (
      <div className={styles.adventCalendar}>
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            minHeight: "100vh",
            fontSize: "18px",
          }}
        >
          Загрузка...
        </div>
      </div>
    );
  }

  if (accessDenied) {
    return (
      <div className={styles.adventCalendar}>
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            alignItems: "center",
            minHeight: "100vh",
            padding: "20px",
            textAlign: "center",
          }}
        >
          <h1
            style={{
              fontSize: "24px",
              marginBottom: "20px",
              color: "#333",
            }}
          >
            Доступ закрыт
          </h1>
          <p
            style={{
              fontSize: "18px",
              color: "#666",
              lineHeight: "1.6",
            }}
          >
            Зарегистрируйся в боте
          </p>
        </div>
      </div>
    );
  }

  if (error && days.length === 0) {
    return (
      <div className={styles.adventCalendar}>
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            minHeight: "100vh",
            fontSize: "18px",
            color: "red",
          }}
        >
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className={styles.adventCalendar}>
      {/* Hero Section with Background Image */}
      <div className={styles.hero}>
        <Image
          src="/assets/images/mainbg.svg"
          alt="DevRel Thanks Advent Calendar"
          fill
          priority
          className={styles.heroImage}
        />
      </div>

      {/* Calendar Card Section */}
      <div className={styles.cardSection}>
        <div className={styles.cardContainer}>
          {/* Navigation Button - Left */}
          <button
            className={`${styles.navButton} ${styles.navButtonLeft}`}
            onClick={handlePrev}
            aria-label="Previous day"
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path
                d="M15 18L9 12L15 6"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </button>

          {/* Date Card */}
          <div
            className={`${styles.dateCard} ${
              currentDayData.status === "opened" ? styles.dateCardOpened : ""
            } ${
              currentDayData.status === "available"
                ? styles.dateCardAvailable
                : ""
            } ${
              currentDayData.status === "locked" ||
              currentDayData.status === "missed"
                ? styles.dateCardDisabled
                : ""
            }`}
            onClick={handleOpenGiftClick}
            style={{
              cursor:
                currentDayData.status === "locked" ||
                currentDayData.status === "missed"
                  ? "default"
                  : "pointer",
            }}
          >
            <div className={styles.dateHeader}>
              <span className={styles.day}>{currentDayData.day}</span>
              <span className={styles.month}>{currentDayData.month}</span>
            </div>

            <div className={styles.giftContainer}>
              <Image
                src={currentDayData.giftImage}
                alt="Gift box"
                width={300}
                height={200}
                className={`${styles.giftImage} ${
                  currentDayData.status === "locked" ||
                  currentDayData.status === "missed"
                    ? styles.giftImageDisabled
                    : ""
                }`}
              />
            </div>
          </div>

          {/* Navigation Button - Right */}
          <button
            className={`${styles.navButton} ${styles.navButtonRight}`}
            onClick={handleNext}
            aria-label="Next day"
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path
                d="M9 18L15 12L9 6"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </button>
        </div>

        {/* Gift action button */}
        <button
          className={`${styles.openButton} ${
            currentDayData.status === "available" ? styles.openButtonActive : ""
          } ${
            currentDayData.status === "locked" ||
            currentDayData.status === "missed"
              ? styles.openButtonDisabled
              : ""
          }`}
          disabled={
            currentDayData.status === "locked" ||
            currentDayData.status === "missed"
          }
          onClick={handleOpenGiftClick}
        >
          {currentDayData.status === "opened"
            ? "Подарок открыт"
            : currentDayData.status === "missed"
            ? "Подарок пропущен"
            : "Открыть подарок"}
        </button>

        {/* Pagination Dots */}
        <div className={styles.pagination}>
          {days.map((_, index) => (
            <button
              key={index}
              className={`${styles.dot} ${
                index === currentDay ? styles.dotActive : ""
              }`}
              onClick={() => setCurrentDay(index)}
              aria-label={`Go to day ${index + 1}`}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default AdventCalendar;
