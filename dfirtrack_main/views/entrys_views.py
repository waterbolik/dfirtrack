from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, ListView
from dfirtrack_main.forms import EntryForm
from dfirtrack_main.logger.default_logger import debug_logger
from dfirtrack_main.models import Entry

class Entrys(LoginRequiredMixin, ListView):
    login_url = '/login'
    model = Entry
    template_name = 'dfirtrack_main/entry/entrys_list.html'
    def get_queryset(self):
        debug_logger(str(self.request.user), " ENTRY_ENTERED")
        return Entry.objects.order_by('entry_id')

class EntrysDetail(LoginRequiredMixin, DetailView):
    login_url = '/login'
    model = Entry
    template_name = 'dfirtrack_main/entry/entrys_detail.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entry = self.object
        entry.logger(str(self.request.user), " ENTRYDETAIL_ENTERED")
        return context

@login_required(login_url="/login")
def entrys_add(request):
    if request.method == 'POST':
        form = EntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.entry_created_by_user_id = request.user
            entry.entry_modified_by_user_id = request.user
            entry.save()
            entry.logger(str(request.user), " ENTRY_ADD_EXECUTED")
            messages.success(request, 'Entry added')
            return redirect('/systems/' + str(entry.system.system_id))
    else:
        if request.method == 'GET' and 'system' in request.GET:
            system = request.GET['system']
            form = EntryForm(initial={
                'system': system,
            })
        else:
            form = EntryForm()
        debug_logger(str(request.user), " ENTRY_ADD_ENTERED")
    return render(request, 'dfirtrack_main/entry/entrys_add.html', {'form': form})

@login_required(login_url="/login")
def entrys_edit(request, pk):
    entry = get_object_or_404(Entry, pk=pk)
    if request.method == 'POST':
        form = EntryForm(request.POST, instance=entry)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.entry_modified_by_user_id = request.user
            entry.save()
            entry.logger(str(request.user), " ENTRY_EDIT_EXECUTED")
            messages.success(request, 'Entry edited')
            return redirect('/systems/' + str(entry.system.system_id))
    else:
        form = EntryForm(instance=entry)
        entry.logger(str(request.user), " ENTRY_EDIT_ENTERED")
    return render(request, 'dfirtrack_main/entry/entrys_edit.html', {'form': form})
