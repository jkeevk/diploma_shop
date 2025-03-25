from jet.dashboard import modules
from jet.dashboard.dashboard import Dashboard, AppIndexDashboard


class YandexMetrikaWidget(modules.DashboardModule):
    """
    Виджет для отображения статистики Яндекс.Метрики в админ-панели.

    Показывает базовые метрики посещаемости. Для реального использования необходимо
    подключить API Яндекс.Метрики.
    """

    title = "Яндекс.Метрика"
    template = "admin/yandex_metrika_widget.html"

    def init_with_context(self, context):
        """
        Инициализация виджета.
        """
        self.data = {"visitors": 1254, "views": 5678}


class CustomIndexDashboard(Dashboard):
    """
    Кастомная главная панель админ-панели Django Jet.

    Включает:
    - Виджет Яндекс.Метрики
    - Список последних действий
    - Быстрый доступ к основным моделям
    """

    def init_with_context(self, context):
        """
        Инициализация панели с контекстом.
        """
        self.children.append(YandexMetrikaWidget())

        self.children.append(
            modules.RecentActions("Последние действия", limit=5, column=0, order=0)
        )

        self.children.append(
            modules.ModelList(
                "Быстрый доступ",
                models=[
                    "backend.models.User",
                    "backend.models.Order",
                    "backend.models.Product",
                ],
                column=1,
                order=0,
            )
        )


class CustomAppIndexDashboard(AppIndexDashboard):
    """
    Кастомная панель для отдельных приложений в админ-панели Django Jet.

    Автоматически показывает модели текущего приложения.
    """

    def init_with_context(self, context):
        """
        Инициализация панели приложения с контекстом.
        """
        self.children.append(
            modules.ModelList(
                title=context["app_label"],
                models=context["app_model_list"],
                column=0,
                order=0,
            )
        )
