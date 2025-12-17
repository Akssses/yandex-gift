"use client";

import { Suspense, useState, useEffect } from "react";
import Image from "next/image";
import Link from "next/link";
import styles from "../gift.module.scss";
import { openGift, getCalendarStatus } from "@/utils/api";
import { getTelegramUserId } from "@/utils/telegram";

const GiftContent17 = () => {
  const [isClaimed, setIsClaimed] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [telegramId, setTelegramId] = useState(null);
  const downloadLink = "https://t.me/addstickers/devrelthanks";

  useEffect(() => {
    const tgId = getTelegramUserId();
    setTelegramId(tgId);
  }, []);

  useEffect(() => {
    const checkGiftStatus = async () => {
      if (!telegramId) return;

      try {
        const calendarStatus = await getCalendarStatus(telegramId);
        const day17Status = calendarStatus.days?.find((day) => day.day === 17);
        if (day17Status?.is_opened || day17Status?.status === "opened") {
          setIsClaimed(true);
        }
      } catch (err) {
        console.error("Error checking gift status:", err);
      }
    };

    checkGiftStatus();
  }, [telegramId]);

  const handleClaimClick = async (e) => {
    e.preventDefault();

    if (!telegramId) {
      setError(
        "Не удалось определить ваш Telegram ID. Откройте страницу через бот."
      );
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      await openGift(telegramId, 17);
      setIsClaimed(true);
    } catch (err) {
      console.error("Error claiming gift:", err);
      if (err.message?.includes("already opened")) {
        setIsClaimed(true);
      } else {
        setError(err.message || "Произошла ошибка при получении подарка");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.giftPage}>
      <div className={styles.giftPageHeader}>
        <Image
          src="/assets/images/гирлянда.svg"
          alt="Гирлянда"
          fill
          className={styles.garlandBackground}
          priority
        />
        <div className={styles.dateBlock}>
          <div className={styles.dateNumber}>17</div>
          <div className={styles.dateMonth}>декабря</div>
        </div>
      </div>

      <div className={styles.xyi}>
        <div className={styles.giftPageContent}>
          {isClaimed ? (
            <>
              <div className={styles.giftPageTitle}>
                Стикерпак для важных переговоров
              </div>
              <div className={styles.giftPageSubtitle}>
                Сегодня мы подготовили для вас стикерпак, который сделает ваши
                чаты ярче и веселее.
              </div>

              <a
                href={downloadLink}
                target="_blank"
                rel="noopener noreferrer"
                className={styles.promoCodeButton}
              >
                <span className={styles.promoCodeText}>Забрать стикеры</span>
              </a>
            </>
          ) : (
            <>
              <div className={styles.giftPageTitle}>
                Стикерпак для важных переговоров
              </div>
              <div className={styles.giftPageSubtitle}>
                Сегодня мы подготовили для вас стикерпак, который сделает ваши
                чаты ярче и веселее.
              </div>
            </>
          )}

          {error && (
            <div
              style={{
                color: "red",
                marginBottom: "1rem",
                textAlign: "center",
              }}
            >
              {error}
            </div>
          )}

          {!isClaimed && (
            <button
              onClick={handleClaimClick}
              disabled={isLoading || !telegramId}
              className={styles.promoCodeButton}
            >
              <span className={styles.promoCodeText}>
                {isLoading ? "Загрузка..." : "Забрать"}
              </span>
            </button>
          )}

          <Link href="/" className={styles.homeButton}>
            На главную
          </Link>
        </div>

        <div className={styles.giftPageSuccessImage}>
          <Image
            src="/assets/images/KV.png"
            alt="Подарок"
            width={358}
            height={280}
          />
        </div>
      </div>
    </div>
  );
};

const GiftPage17 = () => {
  return (
    <Suspense
      fallback={
        <div className={styles.giftPage}>
          <div className={styles.giftPageContent}>
            <div className={styles.giftPageTitle}>Загрузка...</div>
          </div>
        </div>
      }
    >
      <GiftContent17 />
    </Suspense>
  );
};

export default GiftPage17;
