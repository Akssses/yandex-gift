"use client";

import { Suspense, useState, useEffect } from "react";
import Image from "next/image";
import Link from "next/link";
import styles from "../gift.module.scss";
import { checkUser } from "@/utils/api";
import { getTelegramUserId } from "@/utils/telegram";

// Маппинг стека на контент
const stackContentMap = {
  security: {
    image: "/assets/14/Pic_Security.png",
    title: "Суд",
    text: "Суд приносит прозрение и стратегическую внимательность. 2026-й подкинет ситуации, где нужно будет принимать решения быстро и точно — как хороший IDS. Ты увидишь угрозы до того, как они станут инцидентами, и заработаешь репутацию Стража Цифрового Порядка. Истинный хранитель инфраструктурного покоя.",
  },
  analytics: {
    image: "/assets/14/Pic_Analytics.png",
    title: "Солнце",
    text: "Солнце — это чистая аналитическая ясность. В новом году данные будут говорить отчетливо, как если бы сами писали документацию. Ты станешь тем, кто включает свет в переговорках: подсвечиваешь инсайты, объясняешь тренды, приручаешь хаос таблиц. Даже самые упрямые графики станут покорными.",
  },
  backend: {
    image: "/assets/14/Pic_Backend.png",
    title: "Туз Пентаклей",
    text: "2026-й приготовил тебе год фундаментальных апгрейдов и архитектурных откровений. Туз Пентаклей — это когда ресурсы есть, бюджеты сходятся, а сервисы живут дольше, чем мемы про микросервисы. Прими это как знак: оптимизация — не фича, а образ жизни. А Вселенная уже пакует для тебя «performance gifts» — от идеальных индексов до магически зелёных deploy'ев.",
  },
  frontend: {
    image: "/assets/14/Pic_Frontend.png",
    title: "Звезда",
    text: "Звезда приносит светлый, вдохновляющий флоу. В следующем году UI будет собираться «как будто сам», а креатив щёлкать быстрее hot reload'а. Осмелься пробовать новое — анимации, подходы, фреймворки. Ты не просто верстаешь интерфейсы — ты делаешь  красиво.",
  },
  mobile: {
    image: "/assets/14/Pic_Mobile.png",
    title: "Колесо Фортуны",
    text: "Колесо Фортуны обещает захватывающий год смены контекстов: новые SDK, новые платформы, новые «внезапно всё переписали». Но ты вольёшься в этот поток как бог мобильной адаптивности. Лови волну апдейтов, прыгай в новые API — и выходи с релизами, которые собирают звездные ревью в сторе.",
  },
  ai: {
    image: "/assets/14/Pic_AI.png",
    title: "Маг",
    text: "Маг — архетип чистого творчества. В 2026-м ты сможешь воплощать самые смелые AI-идеи, будто у тебя личный GPU-фамильяр. Комбинируй модели, придумывай свои пайплайны, создавай то, что вчера казалось магией. Пусть алгоритмы работают через тебя, а вдохновение — без rate limit'ов.",
  },
  ml: {
    image: "/assets/14/Pic_ML.png",
    title: "Иерофант",
    text: "Иерофант приносит порядок, структуру и глубокие инсайты. 2026-й сделает сложное — понятным, а хитрые модели — почти дружелюбными. Готовься к году обучения: своего, моделей и окружающих. И не стесняйся быть голосом разума, когда все спорят, чья метрика достойна жертвоприношений.",
  },
  product: {
    image: "/assets/14/Pic_Products.png",
    title: "Колесница",
    text: "Колесница — символ драйва и лидерства. В 2026-м ты поведёшь продукт уверенно и красиво, как будто KPI — это дорожные знаки, а спринты — твоя личная трасса. Будет ухабисто? Бывает. Главное — держать руки на руле и не бояться ускоряться, когда видишь правильный вектор.",
  },
  teamlead: {
    image: "/assets/14/Pic_Teamleads.png",
    title: "Сила",
    text: "Сила — это про мягкую мощь. В новом году ты будешь приручать хаос лучше любого фреймворка: эскалации успокаиваются, процессы выстраиваются, команда раскрывается. Твоя эмпатия — твой суперпауэр, а лидерство — тихое, тёплое и очень уверенное. Настоящий Teamlead-дзен.",
  },
  other: {
    image: "/assets/14/Pic_Multistack.png",
    title: "Шут",
    text: "2026 — идеальный год для тех, кто не вписывается в рамки одной профессии. Шут зовёт в новые приключения: проекты, идеи, неожиданные повороты. Позволяй себе экспериментировать, ведь именно на стыке ннаправлений рождаются самые классные штуки.",
  },
};

// Контент по умолчанию (если стек не определен)
const defaultContent = {
  image: "/assets/14/Pic_AI.png",
  title: "Суд",
  text: "Суд приносит прозрение и стратегическую внимательность. 2026-й подкинет ситуации, где нужно будет принимать решения быстро и точно — как хороший IDS. Ты увидишь угрозы до того, как они станут инцидентами, и заработаешь репутацию Стража Цифрового Порядка. Истинный хранитель инфраструктурного покоя.",
};

const GiftContent14 = () => {
  const [content, setContent] = useState(defaultContent);
  const [isLoading, setIsLoading] = useState(true);
  const [telegramId, setTelegramId] = useState(null);

  useEffect(() => {
    // Получаем telegram_id из Telegram WebApp
    const tgId = getTelegramUserId();
    setTelegramId(tgId);
  }, []);

  useEffect(() => {
    // Получаем информацию о пользователе и определяем контент
    const fetchUserContent = async () => {
      if (!telegramId) {
        setIsLoading(false);
        return;
      }

      try {
        const userData = await checkUser(telegramId);
        if (userData?.exists && userData?.position) {
          const stack = userData.position.toLowerCase();
          const stackContent = stackContentMap[stack];
          if (stackContent) {
            setContent(stackContent);
          }
        }
      } catch (err) {
        console.error("Error fetching user data:", err);
        // Используем контент по умолчанию при ошибке
      } finally {
        setIsLoading(false);
      }
    };

    fetchUserContent();
  }, [telegramId]);

  if (isLoading) {
    return (
      <div className={styles.giftPage}>
        <div className={styles.giftPageContent}>
          <div className={styles.giftPageTitle}>Загрузка...</div>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.giftPage}>
      <div className={styles.giftPageHeader14}>
        <Image
          src="/assets/images/гирлянда.svg"
          alt="Гирлянда"
          fill
          className={styles.garlandBackground}
          priority
        />
        <div className={styles.dateBlock14}>
          <img src={content.image} alt={content.title} />
        </div>
      </div>

      <div className={styles.xyi}>
        <div className={styles.giftPageContent}>
          <div className={styles.giftPageTitle}>{content.title}</div>
          <div className={styles.giftPageSubtitle}>{content.text}</div>

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

const GiftPage14 = () => {
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
      <GiftContent14 />
    </Suspense>
  );
};

export default GiftPage14;
