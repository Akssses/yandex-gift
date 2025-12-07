"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import styles from "./AdventCalendar.module.scss";
import { getTelegramUserId } from "@/utils/telegram";
import { getCalendarStatus, openGift } from "@/utils/api";

const AdventCalendar = () => {
  const [currentDay, setCurrentDay] = useState(0);
  const [days, setDays] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const router = useRouter();

  // Загружаем статус календаря при монтировании компонента
  useEffect(() => {
    const loadCalendarStatus = async () => {
      try {
        setLoading(true);

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
            // Если нет telegram_id, используем моковые данные для разработки
            console.warn(
              "Telegram user ID not found after attempts, using mock data"
            );
            console.warn(
              "This means the app is not running in Telegram WebApp or user data is not available"
            );
            console.warn(
              "To test with API, set test_telegram_id in localStorage: localStorage.setItem('test_telegram_id', 'YOUR_TELEGRAM_ID')"
            );
            const mockDays = Array.from({ length: 12 }, (_, i) => ({
              day: String(i + 8).padStart(2, "0"),
              month: "декабря",
              status: i === 0 ? "opened" : i === 1 ? "available" : "locked",
              giftImage:
                i === 0
                  ? "/assets/images/gift.svg"
                  : "/assets/images/gift2.svg",
            }));
            setDays(mockDays);
            setLoading(false);
            return;
          }
        }

        console.log(
          "Fetching calendar status from API for telegram_id:",
          telegramId
        );
        const data = await getCalendarStatus(telegramId);

        console.log("Calendar status from API:", data);
        console.log("Current day from API:", data.current_day);

        // Преобразуем данные из API в формат компонента
        const formattedDays = data.days.map((dayData) => {
          const dayNumber = dayData.day;
          const dayString = String(dayNumber).padStart(2, "0");

          return {
            day: dayString,
            month: "декабря",
            status: dayData.status,
            isOpened: dayData.is_opened,
            giftImage: dayData.is_opened
              ? "/assets/images/gift.svg"
              : "/assets/images/gift2.svg",
          };
        });

        setDays(formattedDays);
        setError(null);
      } catch (err) {
        console.error("Failed to load calendar status:", err);
        setError("Не удалось загрузить календарь");
        // Используем моковые данные при ошибке
        const mockDays = Array.from({ length: 12 }, (_, i) => ({
          day: String(i + 8).padStart(2, "0"),
          month: "декабря",
          status: i === 0 ? "opened" : i === 1 ? "available" : "locked",
          giftImage:
            i === 0 ? "/assets/images/gift.svg" : "/assets/images/gift2.svg",
        }));
        setDays(mockDays);
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
    if (
      !currentDayData ||
      currentDayData.status === "locked" ||
      currentDayData.status === "missed"
    ) {
      return;
    }

    const telegramId = getTelegramUserId();
    const dayNumber = parseInt(currentDayData.day, 10);

    // Если подарок уже открыт, просто переходим на страницу
    if (currentDayData.status === "opened") {
      router.push(`/gift/${dayNumber}`);
      return;
    }

    // Если подарок доступен, открываем его через API
    if (currentDayData.status === "available" && telegramId) {
      try {
        await openGift(telegramId, dayNumber);

        // Обновляем статус локально
        const updatedDays = [...days];
        updatedDays[currentDay] = {
          ...updatedDays[currentDay],
          status: "opened",
          isOpened: true,
          giftImage: "/assets/images/gift.svg",
        };
        setDays(updatedDays);

        // Переходим на страницу подарка
        router.push(`/gift/${dayNumber}`);
      } catch (error) {
        console.error("Failed to open gift:", error);
        alert(error.message || "Не удалось открыть подарок");
      }
    } else if (!telegramId) {
      // Если нет telegram_id, просто переходим на страницу (для разработки)
      router.push(`/gift/${dayNumber}`);
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
