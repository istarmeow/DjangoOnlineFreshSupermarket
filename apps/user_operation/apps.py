from django.apps import AppConfig


class UserOperationConfig(AppConfig):
    name = 'user_operation'
    verbose_name = '操作'

    def ready(self):
        """
        在子类中重写此方法，以便在Django启动时运行代码。
        :return:
        """
        from .signals import userfav_post_save_handler, userfav_pre_delete_handler
