"use client";

import { Suspense } from "react";
import Image from "next/image";
import Link from "next/link";
import styles from "../gift.module.scss";

const GiftContent11 = () => {
  const downloadLink =
    "https://music.yandex.ru/playlists/17b6ac6a-86b5-42ee-a96b-aafcb8669d36?utm_source=web&utm_medium=copy_link";

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
          <div className={styles.dateNumber}>11</div>
          <div className={styles.dateMonth}>декабря</div>
        </div>
      </div>

      <div className={styles.xyi}>
        <div className={styles.giftPageContent}>
          <div className={styles.giftPageTitle}>
            yet another new year playlist
          </div>
          <div className={styles.giftPageSubtitle}>
            Здесь нет очевидных хитов «для фона» — вместо этого электроника,
            гиковская классика, саундтреки, треки про технологии и Новый год на
            разных языках.
            <br />
            <br />
            Пусть следующий год собирается без ошибок, релизы проходят гладко, а
            кофе никогда не заканчивается
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

const GiftPage11 = () => {
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
      <GiftContent11 />
    </Suspense>
  );
};

export default GiftPage11;
