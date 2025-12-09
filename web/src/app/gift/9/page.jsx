"use client";

import { Suspense } from "react";
import Image from "next/image";
import Link from "next/link";
import styles from "../gift.module.scss";

const GiftContent9 = () => {
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
          <div className={styles.dateNumber}>09</div>
          <div className={styles.dateMonth}>декабря</div>
        </div>
      </div>

      <div className={styles.xyi}>
        <div className={styles.giftPageContent}>
          <div className={styles.giftPageTitle}>
            Твой год точно был <br /> насыщенным — доклады, конференции,
            командировки...
          </div>
          <div className={styles.giftPageSubtitle}>
            Когда задачи ещё горят, а в голове уже: «Давайте после праздников».
            Мы собрали простые идей, как оформить рабочее место к Новому году и
            поднять себе настроение — всё внутри PDF.
            <br /> <br />
            Пусть декабрь будет рабочим, но тёплым ✨
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

const GiftPage9 = () => {
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
      <GiftContent9 />
    </Suspense>
  );
};

export default GiftPage9;
