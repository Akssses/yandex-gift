"use client";

import { Suspense } from "react";
import Image from "next/image";
import Link from "next/link";
import styles from "../gift.module.scss";

const GiftContent10 = () => {
  const downloadLink = "https://disk.360.yandex.ru/i/B9KXT8byngsCig";

  return (
    <div className={styles.giftPage}>
      {/* Header section with garland background */}
      <div className={styles.giftPageHeader}>
        <Image
          src="/assets/images/гирлянда.svg"
          alt="Гирлянда"
          fill
          className={styles.garlandBackground}
          priority
        />
        <div className={styles.dateBlock}>
          <div className={styles.dateNumber}>10</div>
          <div className={styles.dateMonth}>декабря</div>
        </div>
      </div>

      <div className={styles.xyi}>
        <div className={styles.giftPageContent}>
          <div className={styles.giftPageTitle}>Самое время добавить киномагии</div>
          <div className={styles.giftPageSubtitle}>
           Лучший план на вечер: горячий напиток и новогодний фильм. Мы собрали подборку картин от Кинопоиска: тёплых, смешных и очень зимних. Выбери фильм, который сделает вечер чуть уютнее!
          </div>

          <a
            href={downloadLink}
            target="_blank"
            rel="noopener noreferrer"
            className={styles.promoCodeButton}
          >
            <span className={styles.promoCodeText}>Забрать</span>
          </a>

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

const GiftPage10 = () => {
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
      <GiftContent10 />
    </Suspense>
  );
};

export default GiftPage10;
