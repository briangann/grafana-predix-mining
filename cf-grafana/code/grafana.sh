#!/bin/bash
wget https://s3-us-west-2.amazonaws.com/grafana-releases/release/grafana-4.6.2.linux-x64.tar.gz
tar xfz grafana-4.6.2.linux-x64.tar.gz
mkdir /home/vcap/app/dashboards
PLUGINSDIR='/home/vcap/app/grafana-4.6.2/data/plugins'
PLUGINSOPT="--pluginsDir $PLUGINSDIR"
mkdir /home/vcap/app/plugins
ulimit -l
sed "s/CF_PORT/$PORT/g" defaults.ini.template > defaults.ini
cat defaults.ini
# copy into conf dir
cp -f defaults.ini grafana-4.6.2/conf/defaults.ini
cd grafana-4.6.2
./bin/grafana-cli $PLUGINSOPT plugins install grafana-azure-monitor-datasource
./bin/grafana-cli $PLUGINSOPT plugins install raintank-worldping-app
./bin/grafana-cli $PLUGINSOPT plugins install neocat-cal-heatmap-panel
./bin/grafana-cli $PLUGINSOPT plugins install satellogic-3d-globe-panel
./bin/grafana-cli $PLUGINSOPT plugins install digiapulssi-breadcrumb-panel
./bin/grafana-cli $PLUGINSOPT plugins install btplc-alarm-box-panel
./bin/grafana-cli $PLUGINSOPT plugins install petrslavotinek-carpetplot-panel
./bin/grafana-cli $PLUGINSOPT plugins install natel-discrete-panel
./bin/grafana-cli $PLUGINSOPT plugins install digiapulssi-organisations-panel
./bin/grafana-cli $PLUGINSOPT plugins install bessler-pictureit-panel
./bin/grafana-cli $PLUGINSOPT plugins install natel-plotly-panel
./bin/grafana-cli $PLUGINSOPT plugins install btplc-trend-box-panel
./bin/grafana-cli $PLUGINSOPT plugins install grafana-piechart-panel
./bin/grafana-cli $PLUGINSOPT plugins install michaeldmoore-annunciator-panel
./bin/grafana-cli $PLUGINSOPT plugins install briangann-gauge-panel
./bin/grafana-cli $PLUGINSOPT plugins install briangann-datatable-panel
./bin/grafana-cli $PLUGINSOPT plugins install jdbranham-diagram-panel
./bin/grafana-cli $PLUGINSOPT plugins install vonage-status-panel
git clone https://github.com/briangann/grafana3-predix-timeseries-datasource.git $PLUGINSDIR/grafana3-predix-timeseries-datasource
./bin/grafana-server
