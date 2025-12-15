"use client";

import { Suspense } from "react";
import Image from "next/image";
import Link from "next/link";
import styles from "../gift.module.scss";

const GiftContent15 = () => {
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
          <div className={styles.dateNumber}>15</div>
          <div className={styles.dateMonth}>декабря</div>
        </div>
      </div>

      <div className={styles.xyi}>
        <div className={styles.giftPageContent}>
          <div className={styles.giftPageTitle}>DevRel Thanks Advent...</div>
          <div className={styles.giftPageSubtitle}>
            ...сегодня на паузе. Возвращайся за сюрпризами завтра 🎄
          </div>

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

const GiftPage15 = () => {
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
      <GiftContent15 />
    </Suspense>
  );
};

export default GiftPage15;
