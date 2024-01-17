def filterStatus(queryset, request):
    if request.query_params.get('status'):
        return queryset.filter(status=request.query_params.get('status'))
    return queryset
def filterSendingStatus(queryset, request):
    if request.query_params.get('status'):
        return queryset.filter(status__in=list(request.query_params.get('status')))
    return queryset
def filterTitle(queryset,request):
    if request.query_params.get('title'):
        return queryset.filter(full_name__startswith = request.query_params.get('title'))
    return queryset
def filterUser(queryset, request):
    if request.query_params.get('user_id'):
        return queryset.filter(user_id=request.query_params.get('user_id'))
    return queryset

def DateFilter(objects, request):
    lowerdate = "2020-01-01"
    higherdate = "2500-01-01"
    if request.query_params.get('created'):
        return objects.filter(created__date = request.query_params.get('created'))
    if request.query_params.get('downdate'):
        lowerdate = request.query_params.get('downdate')
    if request.query_params.get('upperdate'):
        higherdate = request.query_params.get('upperdate')
    return objects.filter(created__range=[lowerdate, higherdate])

def filterModerator(queryset, request):
    if request.query_params.get('moder_id'):
        return queryset.filter(moder_id=request.query_params.get('moder_id'))
    return queryset

def filterReceiver(queryset, request):
    return filterTitle(filterStatus(queryset, request), request)

def filterSending(queryset, request):
    return DateFilter(filterSendingStatus(queryset, request), request)