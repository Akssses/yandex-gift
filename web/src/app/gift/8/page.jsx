"use client";

import { Suspense } from "react";
import Image from "next/image";
import Link from "next/link";
import styles from "../gift.module.scss";

const GiftContent8 = () => {
  const downloadLink =
    "https://disk.360.yandex.ru/d/M5vqMdNsudNk6Q&sa=D&source=editors&ust=1764960640168168&usg=AOvVaw0OxqA1TnRqIm1yt7vxvy3N";

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
          <div className={styles.dateNumber}>08</div>
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
            Лови пак аватарок на все случаи жизни — внутри собрали всё самое
            нужное для tech-амбассадора: «Выступаю на конфе», «Дежурю на
            стенде», «В командировке» и не только. <br /> <br /> Пусть аватарка
            работает за тебя, пока ты работаешь над чем-то классным ✨
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

const GiftPage8 = () => {
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
      <GiftContent8 />
    </Suspense>
  );
};

export default GiftPage8;
