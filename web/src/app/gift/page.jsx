"use client";

import { Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Image from "next/image";
import Link from "next/link";
import { MdContentCopy } from "react-icons/md";
import styles from "./gift.module.scss";

const GiftContent = () => {
  const searchParams = useSearchParams();
  const status = searchParams.get("status") || "new";
  const day = searchParams.get("day") || "09";
  const month = "декабря";
  const promoCode = "YANDEX_PROMOCODE";

  const isOpened = status === "opened";

  return (
    <div className={styles.giftPage}>
      <div className={styles.giftPageBanner}>
        <Image
          src="/assets/images/date-bg.svg"
          alt={`${day} ${month}`}
          width={358}
          height={72}
        />
        <span className={styles.giftPageBannerText}>
          {day} {month}
        </span>
      </div>

      <div className={styles.giftPageContent}>
        <div className={styles.giftPageImagePlaceholder} />

        <div className={styles.giftPageTitle}>
          {isOpened ? "ПОДАРОК ПОЛУЧЕН" : "ВАШ ПОДАРОК:"}
        </div>
        <div className={styles.giftPageSubtitle}>
          промокод на <span>300 рублей</span> в Лавке!
        </div>

        <button
          type="button"
          className={styles.promoCodeButton}
          // TODO: добавить копирование промокода в буфер обмена
        >
          <span className={styles.promoCodeText}>{promoCode}</span>
          <MdContentCopy className={styles.promoCodeIcon} aria-hidden="true" />
        </button>

        <Link href="/" className={styles.homeButton}>
          На главную
        </Link>
      </div>

      <div className={styles.giftPageSuccessImage}>
        <Image
          src="/assets/images/success.svg"
          alt="Подарок успешно открыт"
          width={358}
          height={280}
        />
      </div>
    </div>
  );
};

const GiftPage = () => {
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
      <GiftContent />
    </Suspense>
  );
};

export default GiftPage;
