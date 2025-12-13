"use client";

import { Suspense } from "react";
import Image from "next/image";
import Link from "next/link";
import styles from "../gift.module.scss";

const GiftContent13 = () => {
  const downloadLink = "https://disk.360.yandex.ru/i/OjdruO9xMko_Nw";

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
          <div className={styles.dateNumber}>13</div>
          <div className={styles.dateMonth}>декабря</div>
        </div>
      </div>

      <div className={styles.xyi}>
        <div className={styles.giftPageContent}>
          <div className={styles.giftPageTitle}>Если вы готовитесь к...</div>
          <div className={styles.giftPageSubtitle}>
            ...выступлению любого уровня, загляните по ссылке — там собраны
            полезные слайды, универсальный шаблон для конференций и занятия,
            которые помогают расти: от базовой подготовки до выходов на
            международную сцену, работы с питчем и преодоления барьеров
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

const GiftPage13 = () => {
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
      <GiftContent13 />
    </Suspense>
  );
};

export default GiftPage13;
