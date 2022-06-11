from django.contrib import admin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse

from django_object_actions import DjangoObjectActions

from debts import constants as debt_constants
from debts.admin_utils import ObjectActionsController
from debts.models import Debt, DebtRequest, ClosedDebtRequest
from debts.services import (
    DebtRequestUpdateStatusService,
    CreateClosedDebtRequestService,
)


class IsActiveListFilter(admin.SimpleListFilter):
    title = "active"
    parameter_name = "is_active"

    STATUS_TRUE = 'true'
    STATUS_FALSE = 'false'

    def lookups(self, request, model_admin):
        return (
            (self.STATUS_TRUE, 'True'),
            (self.STATUS_FALSE, 'False')
        )

    def queryset(self, request, queryset):
        pass


class IsActiveDebtListFilter(IsActiveListFilter):
    def queryset(self, request, queryset):
        if self.value() == self.STATUS_TRUE:
            return queryset.filter(closed_request__is_closed=False)

        if self.value() == self.STATUS_FALSE:
            return queryset.filter(
                Q(closed_request__isnull=True) | Q(closed_request__is_closed=True)
            )


@admin.register(Debt)
class DebtAdmin(DjangoObjectActions, admin.ModelAdmin):
    list_display = ('__str__', 'is_active', 'created')
    list_filter = (IsActiveDebtListFilter,)
    search_fields = ['creditor__username', 'debtor__username']
    search_help_text = "Search through creditor/debtor name"

    fieldsets = (
        (None, {
            'fields': (
                'id', 'creditor', 'debtor',
                'money', 'description', 'created',
            ),
        }),
    )
    readonly_fields = ('id', 'created')

    action_controller = ObjectActionsController()

    @action_controller.show_when(lambda obj: obj.closed_request is None)
    def close_as_debtor(self, request, obj):
        CreateClosedDebtRequestService(
            debt_id=obj.pk,
            creator=request.user,
        ).close_as_debtor()

    @action_controller.show_when(lambda obj: obj.closed_request is None)
    def close_as_creditor(self, request, obj):
        CreateClosedDebtRequestService(
            debt_id=obj.pk,
            creator=request.user,
        ).close_as_creditor()

    @action_controller.show_when(lambda obj: obj.from_request)
    def connected_debt_request(self, request, obj):
        return HttpResponseRedirect(
            reverse("admin:debts_debtrequest_change", args=(obj.from_request.id,))
        )

    @action_controller.show_when(lambda obj: obj.closed_request)
    def connected_closed_debt_request(self, request, obj):
        return HttpResponseRedirect(
            reverse("admin:debts_closeddebtrequest_change", args=(obj.closed_request.id,))
        )

    change_actions = action_controller.change_actions

    def get_change_actions(self, request, object_id, _):
        obj = self.get_object(request, object_id)
        return self.action_controller.filter_by_object(obj)

    def has_change_permission(self, request, obj=None):
        return obj and obj.is_active

    def has_delete_permission(self, request, obj=None):
        return False


class IsActiveDebtRequestListFilter(IsActiveListFilter):
    def queryset(self, request, queryset):
        if self.value() == self.STATUS_TRUE:
            return queryset.filter(connected_debt__isnull=True, declined=False)

        if self.value() == self.STATUS_FALSE:
            return queryset.filter(Q(declined=True) | Q(connected_debt__isnull=False))


@admin.register(DebtRequest)
class DebtRequestAdmin(DjangoObjectActions, admin.ModelAdmin):
    list_display = ('__str__', 'is_active', 'declined', 'created')
    list_filter = (IsActiveDebtRequestListFilter,)
    search_fields = ['creditor__username', 'debtor__username']
    search_help_text = "Search through creditor/debtor name"
    fieldsets = (
        (None, {
            'fields': (
                'id', 'creditor', 'debtor', 'creator',
                'money', 'declined', 'description',
                'created',
            ),
        }),
    )
    readonly_fields = (
        'id', 'created', 'declined',
    )

    action_controller = ObjectActionsController()

    @action_controller.show_when(lambda obj: obj.is_active)
    def accept_request(self, request, obj):
        DebtRequestUpdateStatusService(
            debt_request_id=obj.pk,
            status=debt_constants.STATUS_ACCEPT,
            creator=request.user,
        ).update_debt_request_from_admin()

    @action_controller.show_when(lambda obj: obj.is_active)
    def decline_request(self, request, obj):
        DebtRequestUpdateStatusService(
            debt_request_id=obj.pk,
            status=debt_constants.STATUS_DECLINE,
            creator=request.user,
        ).update_debt_request_from_admin()

    @action_controller.show_when(lambda obj: not obj.is_active and not obj.declined)
    def connected_debt(self, request, obj):
        return HttpResponseRedirect(
            reverse("admin:debts_debt_change", args=(obj.connected_debt.id,))
        )

    change_actions = action_controller.change_actions

    def get_change_actions(self, request, object_id, _):
        obj = self.get_object(request, object_id)
        return self.action_controller.filter_by_object(obj)

    def has_change_permission(self, request, obj=None):
        return obj and obj.is_active

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ClosedDebtRequest)
class ClosedDebtRequestAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'from_debt', 'is_closed')

    fieldsets = (
        (None, {
            'fields': (
                'id', 'is_closed',
                'created', 'closed',
            ),
        }),
    )

    readonly_fields = (
        'id', 'is_closed', 'created', 'closed',
    )

    action_controller = ObjectActionsController()

    @action_controller.show_when(lambda obj: not obj.is_closed)
    def close_debt(self, request, obj):
        obj.close()

    @action_controller.show_when(lambda obj: obj.from_debt)
    def connected_debt(self, request, obj):
        return HttpResponseRedirect(
            reverse("admin:debts_debt_change", args=(obj.from_debt.id,))
        )

    change_actions = action_controller.change_actions

    def get_change_actions(self, request, object_id, _):
        obj = self.get_object(request, object_id)
        return self.action_controller.filter_by_object(obj)

    def has_change_permission(self, request, obj=None):
        return obj and not obj.is_closed

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.disable_action('delete_selected')
