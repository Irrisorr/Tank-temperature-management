import plotly.graph_objects as ply
import numpy as np
from dash import Dash, dcc, html, Input, Output, State


t = [0.0]       #czas dokonania pomiaru
temp_na_polu = 291     #temperatura na polu [K]
wsp_przenikania_ciepla = 0.025    #współczynnik przenikania ciepła
S = 60 #pole powierzchni tafli wody (w metrach kwadratowych)
h = 1.5   #głebokosc basenu (w metrach)
Tp = 1        #okres próbkowania
t_sim = 7200        #czas przez jaki ma działać system i dokonywać pomiarów
N=int(t_sim/Tp)+1       #ilość pomiarów do wykonania
temp=[temp_na_polu] #temperatura w zbiorniku
Qd=[0.0] #dostarczane ciepło
Qo=[0.0]  #uciekające ciepło
c = 4200  #pojemnosc cieplna wody[J/kgK]
m = S * h * 1000  #masa wody w basenie (1 litr = 1 kilo)
tempmin = temp_na_polu    #minimalna możliwa temperatura w basenie
tempmax = 373   #maksymalna do osiągnięcia wysokość cieczy w naczyniu
temp_n = 310   #temperatura jaka ma być
temp_zadana = []      #temperatura jaka ma byc w postaci tabeli na potrzebe wykresu
kp=0.02     #wzmocnienie regulatora (od 0.01 do 0.025) nie wiem co to oznacza
Ti= 15.0         #stała całkowania   (od 5 do 25)
umax = 10.0  #sygnal sterujacy maksymalny
umin = 0.0  #sygnal sterujacy minamlny
n_grz = 10   #ilosc grzałek
Qd_max = 100000   #maksymalna moc grzałek [W]
Qd_min = 0.0    #minimalna moc grzałek [W]
e = []      #uchyb regulacji
u_p = []    #regulator typu P
u_pi = []   #regulator typu PI

for n in range(1, N):
    t.append(n*Tp)      #czas zrobienia pomiaru w sekundach
    temp_zadana.append(temp_n)  #temperatura na rzecz wykresów
    e.append(temp_n - temp[-1])      #aktualizacja uchybu regulacji (różnica miedzy tym co jest,a tym co powinno byc)
    #Regulatory
    u_p.append(min(max((Tp / Ti) * sum(e), umin), umax))    #Regulator P
    u_pi.append(kp * (e[-1] + ((Tp / Ti) * sum(e))))        #Regulator PI

    #Automatyzacja dostarczanego ciepła i wykaz temperatury
    Qo.append(wsp_przenikania_ciepla * S * (temp[- 1] - temp_na_polu))  #uciekające ciepło
    Qd.append((((Qd_max - Qd_min) * (u_pi[-1] - umin)) / (umax - umin)) + Qd_min)  #moc grzałek
    temp.append(max(min(((Tp*(((n_grz * Qd[-1]) - Qo[-1]) / (m * c))) + temp[-1]), tempmax), tempmin))      #wysokosc cieczy w danej sekundzie pomiaru


fig = ply.Figure(
    layout=dict(
        title="Regulator",
        yaxis_type="linear",
        yaxis_range=[-0.2, 100],
        xaxis_title="czas [s]",
        yaxis_title="Sygnał",
    )
)
fig.add_trace(ply.Scatter(x=t, y=u_p, mode='markers', name="Regulator typu P", marker=dict(color='royalblue', size=3)))
fig.add_trace(ply.Scatter(x=t, y=u_pi, name="Regulator typu PI", line=dict(width=2)))
#fig.show()

fig2 = ply.Figure(
    layout=dict(
        title="Ciepło",
        yaxis_type="linear",
        yaxis_range=[-0.2, 50000],
        xaxis_title="czas [s]",
        yaxis_title="Moc",
    )
)
fig2.add_trace(ply.Scatter(x=t, y=Qd, mode='markers', name="Ciepło dawane", marker=dict(color='royalblue', size=3)))
fig2.add_trace(ply.Scatter(x=t, y=Qo, name="Ciepło ulatujące", line=dict(width=2)))
#fig2.show()

fig3 = ply.Figure(
    layout=dict(
        title="Temperatura",
        yaxis_type="linear",
        yaxis_range=[273, 350],
        xaxis_title="czas [s]",
        yaxis_title="Temperatura [K]",
    )
)
fig3.add_trace(ply.Scatter(x=t, y=temp, mode='markers', name="temperatura w zbiorniku", marker=dict(color='royalblue', size=3)))
fig3.add_trace(ply.Scatter(x=t, y=temp_zadana, name="temperatura zadana", line=dict(width=2)))
#fig3.show()

app = Dash(__name__)

app.layout = html.Div([
    html.H2('Sterowanie temperaturą w basenie'),
    html.H5('Obecna temperatura'),
    dcc.Slider(15, 30, 1, value=18, id='starttemp'),
    html.H5('Docelowa temperatura'),
    dcc.Slider(20, 40, 1, value=33, id='endtemp'),
    html.H5('Wzmocnienie regulatora'),
    dcc.Slider(0.01, 0.025, 0.001, value=0.02, id='nkp'),
    html.H5('Stała całkowania'),
    dcc.Slider(5, 25, 1, value=15, id='nti'),
    dcc.Graph(id='firstGraph', figure=fig),
    dcc.Graph(id='secondGraph', figure=fig2),
    dcc.Graph(id='thirdGraph', figure=fig3),
])

@app.callback([Output('firstGraph', 'figure'),
                Output('secondGraph', 'figure'),
                Output('thirdGraph', 'figure'),
            ],
              [
              Input('starttemp', 'value'),
              Input('endtemp', 'value'),
              Input('nkp', 'value'),
              Input('nti', 'value')]
              )
def updateFig(startTemp, endTemp, nkp, nti):
    
    startTemp = startTemp + 273
    endTemp = endTemp + 273
    t = [0.0]       #czas dokonania pomiaru
    temp_na_polu = startTemp   #temperatura na polu [K]
    wsp_przenikania_ciepla = 0.025    #współczynnik przenikania ciepła
    S = 60 #pole powierzchni tafli wody (w metrach kwadratowych)
    h = 1.5   #głebokosc basenu (w metrach)
    Tp = 1        #okres próbkowania
    t_sim = 7200        #czas przez jaki ma działać system i dokonywać pomiarów
    N=int(t_sim/Tp)+1       #ilość pomiarów do wykonania
    temp=[temp_na_polu] #temperatura w zbiorniku
    Qd=[0.0] #dostarczane ciepło
    Qo=[0.0]  #uciekające ciepło
    c = 4200  #pojemnosc cieplna wody[J/kgK]
    m = S * h * 1000  #masa wody w basenie (1 litr = 1 kilo)
    tempmin = temp_na_polu    #minimalna możliwa temperatura w basenie
    tempmax = 373   #maksymalna do osiągnięcia wysokość cieczy w naczyniu
    temp_n = endTemp   #temperatura jaka ma być
    temp_zadana = []      #temperatura jaka ma byc w postaci tabeli na potrzebe wykresu
    kp=nkp   #wzmocnienie regulatora (od 0.01 do 0.025) nie wiem co to oznacza
    Ti= nti        #stała całkowania   (od 5 do 25)
    umax = 10.0  #sygnal sterujacy maksymalny
    umin = 0.0  #sygnal sterujacy minamlny
    n_grz = 10   #ilosc grzałek
    Qd_max = 100000   #maksymalna moc grzałek [W]
    Qd_min = 0.0    #minimalna moc grzałek [W]
    e = []      #uchyb regulacji
    u_p = []    #regulator typu P
    u_pi = []   #regulator typu PI
    for n in range(1, N):
        t.append(n*Tp)      #czas zrobienia pomiaru w sekundach
        temp_zadana.append(temp_n)  #temperatura na rzecz wykresów
        e.append(temp_n - temp[-1])      #aktualizacja uchybu regulacji (różnica miedzy tym co jest,a tym co powinno byc)
        #Regulatory
        u_p.append(min(max((Tp / Ti) * sum(e), umin), umax))    #Regulator P
        u_pi.append(kp * (e[-1] + ((Tp / Ti) * sum(e))))        #Regulator PI

        #Automatyzacja dostarczanego ciepła i wykaz temperatury
        
        Qo.append(wsp_przenikania_ciepla * S * (temp[- 1] - temp_na_polu))  #uciekające ciepło
        Qd.append((((Qd_max - Qd_min) * (u_pi[-1] - umin)) / (umax - umin)) + Qd_min)  #moc grzałek
        temp.append(max(min(((Tp*(((n_grz * Qd[-1]) - Qo[-1]) / (m * c))) + temp[-1]), tempmax), tempmin))      #wysokosc cieczy w danej sekundzie pomiaru
        #print(n)
    fig.update_traces(x=t, y=u_p, selector=dict(name="Regulator typu P"))
    fig.update_traces(x=t, y=u_pi, selector=dict(name="Regulator typu PI"))
    fig2.update_traces(x=t, y=Qd, selector=dict(name="Ciepło dawane"))
    fig2.update_traces(x=t, y=Qo, selector=dict(name="Ciepło ulatujące"))
    fig3.update_traces(x=t, y=temp, selector=dict(name="temperatura w zbiorniku"))
    fig3.update_traces(x=t, y=temp_zadana, selector=dict(name="temperatura zadana"))
    print('updated')
    return fig, fig2, fig3

if __name__ == '__main__':
    app.run_server(debug=True)