"use client";

import { Suspense } from "react";
import Image from "next/image";
import Link from "next/link";
import styles from "../gift.module.scss";

const GiftContent9 = () => {
  const downloadLink = "https://disk.360.yandex.ru/i/B9KXT8byngsCig";

  return (
    <div className={styles.giftPage}>
      <div className={styles.giftPageBanner}>
        <Image
          src="/assets/dates/9.svg"
          alt="9 декабря"
          width={358}
          height={72}
        />
      </div>

      <div className={styles.giftPageContent}>
        <div className={styles.giftPageTitle}>
          Когда задачи ещё горят, а в голове уже: «Давайте после праздников».
        </div>
        <div className={styles.giftPageSubtitle}>
          Мы собрали простые идей, как оформить рабочее место к Новому году и
          поднять себе настроение — всё внутри PDF.
          <br />
          <br />
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
