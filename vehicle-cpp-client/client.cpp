#include <grpcpp/grpcpp.h>
#include "vehicle_data.grpc.pb.h"
#include <thread>
#include <chrono>
#include <iomanip>
#include <sstream>
#include <cstdlib>
#include <iostream>
#include <stdexcept>

using grpc::Channel;
using grpc::ClientContext;
using grpc::Status;
using grpc::ClientWriter;

using namespace std;

class VehicleDataStreamerClient {
public:
    VehicleDataStreamerClient(shared_ptr<Channel> channel)
        : stub_(vehicle::VehicleDataStreamer::NewStub(channel)) {}

    void StreamData() {
        
        ClientContext context;
        vehicle::StreamResponse response;
        unique_ptr<ClientWriter<vehicle::VehicleData>> writer(
            stub_->StreamVehicleData(&context, &response));

        // Generate dummy data every second and send
        while(true) {
            vehicle::VehicleData data;
            GenerateDummyData(data);
            writer->Write(data);

            cout << "Sent vehicle data for vehicle: " << data.vehicle_id() << endl;
            this_thread::sleep_for(chrono::seconds(1));
        }

        writer->WritesDone();
        Status status = writer->Finish();

        if (status.ok()) {
            cout << "Data stream completed successfully" << endl;
        } else {
            cout << "Stream failed: " << status.error_message() << endl;
        }
    }

private:
    unique_ptr<vehicle::VehicleDataStreamer::Stub> stub_;

    void GenerateDummyData(vehicle::VehicleData& data) {
        data.set_vehicle_id(getRandomVehicleID());
        data.set_timestamp(get_current_timestamp());
        
        // Telemetry data
        vehicle::TelemetryData* telemetry = data.mutable_telemetry();
        telemetry->set_speed(rand() % 120 + 30);    
        telemetry->set_rpm(rand() % 7000 + 1000);   
        telemetry->set_fuel_level(rand() % 100);   
        telemetry->set_engine_temp(rand() % 120 + 60);   
        telemetry->set_battery_voltage(12.6);   
        telemetry->set_odometer(50000 + rand() % 1000);   

        // // GPS data
        // vehicle::GpsData* gps = data.mutable_gps();
        // gps->set_latitude(getRandomFloat(-90.0, 90.0));   
        // gps->set_longitude(getRandomFloat(-180.0, 180.0));   
        // gps->set_altitude(getRandomFloat(25, 40));   
        // gps->set_speed_over_ground(rand() % 100);   
        // gps->set_heading(rand() % 360);   

        // // Diagnostic data
        // vehicle::DiagnosticData* diagnostics = data.mutable_diagnostics();
        // diagnostics->add_dtc_codes("P0420");   
        // diagnostics->set_engine_load(rand() % 100);   
        // diagnostics->set_throttle_position(rand() % 100);   
        // diagnostics->set_transmission_temp(getRandomFloat(70, 90));   
        // diagnostics->set_tire_pressure(getRandomFloat(25, 40));   

        // // Driver behavior data
        // vehicle::DriverBehaviorData* driver_behavior = data.mutable_driver_behavior();
        // driver_behavior->set_acceleration(rand() % 10);   
        // driver_behavior->set_deceleration(rand() % 10);   
        // driver_behavior->set_steering_angle(rand() % 180);   
        // driver_behavior->set_seatbelt_fastened(true);
        // driver_behavior->set_airbag_deployed(false);

        // // Infotainment data
        // vehicle::InfotainmentData* infotainment = data.mutable_infotainment();
        // infotainment->set_media_playing("XYZ Radio Station");
        // infotainment->set_bluetooth_connected(true);
        // infotainment->add_connected_devices("Device_123");
    }

    string getRandomVehicleID() {
        static const string vehicle_ids[] = {
            "ABC123", "DEF456", "GHI789", "JKL012", "MNO345",
            "PQR678", "STU901", "VWX234", "YZA567", "BCD890"
        };
        int random_index = rand() % 10;
        return vehicle_ids[random_index];
    }

    string get_current_timestamp() {
        auto now = chrono::system_clock::now();
        auto now_c = chrono::system_clock::to_time_t(now);

        // Convert to tm structure
        tm tm = *localtime(&now_c);

        // Format the time into a string
        ostringstream oss;
        oss << put_time(&tm, "%Y-%m-%dT%H:%M:%S"); // ISO 8601 format
        return oss.str();
    }

    float getRandomFloat(float min, float max) {
        return min + static_cast<float>(rand()) / (static_cast<float>(RAND_MAX / (max - min)));
    }
};

string getGrpcServerAddress() {
    const char* grpc_server = getenv("GRPC_SERVER");
    if (grpc_server == nullptr) {
        throw runtime_error("grpc_server not provided in environment variable.");
    }
    return string(grpc_server);
}

int main(int argc, char** argv) {

    try {
        cout << "==========   Starting Vehicle Data Streamer Client   ==========" << endl;

        string grpc_server = getGrpcServerAddress();

        VehicleDataStreamerClient client(
            grpc::CreateChannel(
                grpc_server, 
                grpc::InsecureChannelCredentials()
            )
        );
        cout << "Streaming data to " << grpc_server << " ..." << endl;
        client.StreamData();
    }
    catch(const exception& e) {
        cerr << "Execption occurred: " << e.what() << endl;
    }

    return 0;
}
