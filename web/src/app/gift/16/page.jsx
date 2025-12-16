"use client";

import { Suspense, useState, useEffect } from "react";
import Image from "next/image";
import Link from "next/link";
import styles from "../gift.module.scss";
import { claimPromoCode, getCalendarStatus } from "@/utils/api";
import { getTelegramUserId } from "@/utils/telegram";

const GiftContent16 = () => {
  const [isClaimed, setIsClaimed] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [telegramId, setTelegramId] = useState(null);

  useEffect(() => {
    // Получаем telegram_id из Telegram WebApp
    const tgId = getTelegramUserId();
    setTelegramId(tgId);
  }, []);

  useEffect(() => {
    // Проверяем, получил ли пользователь уже промокод при загрузке страницы
    const checkPromoCodeStatus = async () => {
      if (!telegramId) {
        return;
      }

      try {
        const calendarStatus = await getCalendarStatus(telegramId);
        // Проверяем, открыт ли день 16
        const day16Status = calendarStatus.days?.find((day) => day.day === 16);
        if (day16Status?.is_opened || day16Status?.status === "opened") {
          setIsClaimed(true);
        }
      } catch (err) {
        // Игнорируем ошибки при проверке статуса, чтобы не показывать ошибку пользователю
        console.error("Error checking promo code status:", err);
      }
    };

    checkPromoCodeStatus();
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
      await claimPromoCode(telegramId, 16);
      setIsClaimed(true);
    } catch (err) {
      console.error("Error claiming promo code:", err);
      setError(err.message || "Произошла ошибка при получении промокода");
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
          <div className={styles.dateNumber}>16</div>
          <div className={styles.dateMonth}>декабря</div>
        </div>
      </div>

      <div className={styles.xyi}>
        <div className={styles.giftPageContent}>
          {isClaimed ? (
            <>
              <div className={styles.giftPageTitle}>
                Подарок пришел вам в бот!
              </div>
              <div className={styles.giftPageSubtitle}>
                Проверьте сообщения.
              </div>
            </>
          ) : (
            <>
              <div className={styles.giftPageTitle}>
                Промокод на Яндекс Маркет
              </div>
              <div className={styles.giftPageSubtitle}>
                Самое время подумать о новогодней атмосфере: заказать гирлянду
                или обновить украшения (или заказать ещё больше подарков на
                Новый год)
                <br />
                <br />
                Если воспользоваться промокодом в течение года не получится
                лично, им можно порадовать друзей в России.
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

const GiftPage16 = () => {
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
      <GiftContent16 />
    </Suspense>
  );
};

export default GiftPage16;
