"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import styles from "./AdventCalendar.module.scss";

const AdventCalendar = () => {
  const [currentDay, setCurrentDay] = useState(0);
  const router = useRouter();

  // Mock data for calendar days (December 8-19)
  const days = Array.from({ length: 12 }, (_, i) => ({
    day: String(i + 8).padStart(2, "0"), // Start from day 8
    month: "декабря",
    // 08 – подарок уже открыт
    // 09 – можно открыть подарок
    // 10–19 – нельзя открыть подарок (кнопка серая, не кликабельная)
    status: i === 0 ? "opened" : i === 1 ? "available" : "locked",
    // Картинка:
    // - только открытые карточки – цветной gift.svg
    // - карточки открытия (available/locked) – gift2.svg
    giftImage: i === 0 ? "/assets/images/gift.svg" : "/assets/images/gift2.svg",
  }));

  const handleNext = () => {
    setCurrentDay((prev) => (prev + 1) % days.length);
  };

  const handlePrev = () => {
    setCurrentDay((prev) => (prev - 1 + days.length) % days.length);
  };

  const currentDayData = days[currentDay];

  const handleOpenGiftClick = () => {
    if (currentDayData.status === "available") {
      router.push(`/gift?day=${currentDayData.day}&status=new`);
    } else if (currentDayData.status === "opened") {
      router.push(`/gift?day=${currentDayData.day}&status=opened`);
    }
  };

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
              currentDayData.status === "locked" ? styles.dateCardDisabled : ""
            }`}
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
                  currentDayData.status === "locked"
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
            currentDayData.status === "locked" ? styles.openButtonDisabled : ""
          }`}
          disabled={currentDayData.status === "locked"}
          onClick={handleOpenGiftClick}
        >
          {currentDayData.status === "opened"
            ? "Подарок открыт"
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
