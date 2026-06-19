from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
import pandas as pd
import plotly.express as px
from .forms import RegisterForm, FishingSpotForm, FishingTripForm, CalculatorForm
from .models import Angler, FishingSpot, FishingTrip


def get_angler_or_redirect(request):
    try:
        return request.user.angler, None
    except Angler.DoesNotExist:
        return None, redirect('home')


def home(request):
    return render(request, 'diary/home.html')


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Angler.objects.create(
                user=user,
                region=form.cleaned_data['region'],
                favorite_fish=form.cleaned_data.get('favorite_fish', ''),
            )
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'diary/register.html', {'form': form})


@login_required
def dashboard(request):
    angler, redirect_response = get_angler_or_redirect(request)
    if redirect_response:
        return redirect_response

    trips = angler.trips.all()
    spots = angler.spots.all()

    kpi = None
    chart_monthly = None
    chart_spots = None
    chart_correlation = None
    chart_moon = None
    stats_table = None

    if trips.exists():
        data = [{
            'date': t.date,
            'spot': t.spot.name,
            'water_temp': float(t.water_temp),
            'pressure': t.pressure,
            'moon_phase': t.get_moon_phase_display(),
            'catch_weight_kg': float(t.catch_weight_kg),
            'bite_score': t.bite_score,
        } for t in trips]

        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.to_period('M').astype(str)

        best_spot_row = df.groupby('spot')['catch_weight_kg'].sum().sort_values(ascending=False)
        kpi = {
            'total_catch': round(df['catch_weight_kg'].sum(), 2),
            'trips_count': len(df),
            'best_score': int(df['bite_score'].max()),
            'best_spot': best_spot_row.index[0] if len(best_spot_row) else '—',
        }

        monthly = df.groupby('month')['catch_weight_kg'].sum().reset_index()
        monthly.columns = ['Месяц', 'Улов (кг)']
        fig1 = px.bar(monthly, x='Месяц', y='Улов (кг)', title='Улов по месяцам', color_discrete_sequence=['#1976a3'])
        fig1.update_layout(plot_bgcolor='white', paper_bgcolor='white')
        chart_monthly = fig1.to_html(full_html=False, include_plotlyjs='cdn')

        by_spot = df.groupby('spot').agg(
            avg_catch=('catch_weight_kg', 'mean'),
            trips_count=('catch_weight_kg', 'count'),
        ).round(2).reset_index()
        by_spot.columns = ['Водоём', 'Средний улов (кг)', 'Кол-во выездов']
        fig2 = px.bar(by_spot, x='Водоём', y='Средний улов (кг)', title='Средний улов по водоёмам', hover_data=['Кол-во выездов'], color_discrete_sequence=['#4fb8a3'])
        fig2.update_layout(plot_bgcolor='white', paper_bgcolor='white')
        chart_spots = fig2.to_html(full_html=False, include_plotlyjs=False)

        fig3 = px.scatter(df, x='bite_score', y='catch_weight_kg', title='Прогноз vs реальный улов', labels={'bite_score': 'Балл клёва', 'catch_weight_kg': 'Улов (кг)'}, color_discrete_sequence=['#0d4f6e'])
        fig3.update_traces(marker=dict(size=14, line=dict(width=1, color='white')))
        fig3.update_layout(plot_bgcolor='white', paper_bgcolor='white')
        chart_correlation = fig3.to_html(full_html=False, include_plotlyjs=False)

        moon = df.groupby('moon_phase')['catch_weight_kg'].sum().reset_index()
        moon.columns = ['Фаза', 'Улов']
        fig4 = px.pie(moon, names='Фаза', values='Улов', title='Распределение улова по фазам луны', color_discrete_sequence=['#1976a3', '#4fb8a3', '#7dd3c0', '#0d4f6e'])
        fig4.update_layout(paper_bgcolor='white')
        chart_moon = fig4.to_html(full_html=False, include_plotlyjs=False)

        stats = df.groupby('spot').agg(
            count=('catch_weight_kg', 'count'),
            total=('catch_weight_kg', 'sum'),
            avg=('catch_weight_kg', 'mean'),
            best=('catch_weight_kg', 'max'),
            avg_score=('bite_score', 'mean'),
        ).round(2).reset_index()
        stats.columns = ['Водоём', 'Выездов', 'Всего улов (кг)', 'Средний (кг)', 'Лучший (кг)', 'Средний балл']
        stats_table = stats.to_html(classes='table table-striped', index=False)

    return render(request, 'diary/dashboard.html', {
        'angler': angler,
        'trips': trips,
        'spots': spots,
        'kpi': kpi,
        'chart_monthly': chart_monthly,
        'chart_spots': chart_spots,
        'chart_correlation': chart_correlation,
        'chart_moon': chart_moon,
        'stats_table': stats_table,
    })


@login_required
def spot_add(request):
    angler, redirect_response = get_angler_or_redirect(request)
    if redirect_response:
        return redirect_response
    if request.method == 'POST':
        form = FishingSpotForm(request.POST)
        if form.is_valid():
            spot = form.save(commit=False)
            spot.angler = angler
            spot.save()
            return redirect('dashboard')
    else:
        form = FishingSpotForm()
    return render(request, 'diary/spot_form.html', {'form': form})


@login_required
def trip_add(request):
    angler, redirect_response = get_angler_or_redirect(request)
    if redirect_response:
        return redirect_response
    if request.method == 'POST':
        form = FishingTripForm(request.POST, angler=angler)
        if form.is_valid():
            trip = form.save(commit=False)
            trip.angler = angler
            trip.save()
            return redirect('dashboard')
    else:
        form = FishingTripForm(angler=angler)
    return render(request, 'diary/trip_form.html', {'form': form})


def calculator(request):
    result = None
    if request.method == 'POST':
        form = CalculatorForm(request.POST)
        if form.is_valid():
            temp = float(form.cleaned_data['water_temp'])
            pressure = form.cleaned_data['pressure']
            moon = form.cleaned_data['moon_phase']

            score = 0
            if 15 <= temp <= 22:
                score += 4
            elif 10 <= temp < 15 or 22 < temp <= 26:
                score += 2
            elif 5 <= temp < 10 or 26 < temp <= 30:
                score += 1

            if 745 <= pressure <= 755:
                score += 3
            elif 740 <= pressure < 745 or 755 < pressure <= 760:
                score += 2
            elif 735 <= pressure < 740 or 760 < pressure <= 765:
                score += 1

            moon_coef = {'new': 3, 'waxing': 2, 'full': 1, 'waning': 2}
            score += moon_coef.get(moon, 0)
            score = min(score, 10)

            if score >= 7:
                color = 'success'
                verdict = 'Отличный день для рыбалки!'
            elif score >= 4:
                color = 'warning'
                verdict = 'Средние шансы на клёв'
            else:
                color = 'danger'
                verdict = 'Лучше остаться дома'

            result = {'score': score, 'color': color, 'verdict': verdict, 'percent': score * 10}
    else:
        form = CalculatorForm()
    return render(request, 'diary/calculator.html', {'form': form, 'result': result})