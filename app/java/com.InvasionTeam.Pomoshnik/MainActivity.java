package com.InvasionTeam.Pomoshnik;

import androidx.appcompat.app.AppCompatActivity;
import android.content.Intent;
import android.os.Bundle;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import com.vk.api.sdk.VK;
import com.vk.api.sdk.auth.VKAccessToken;
import com.vk.api.sdk.auth.VKAuthCallback;
import com.vk.api.sdk.auth.VKScope;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;

import java.util.Arrays;
import java.util.List;

public class MainActivity extends AppCompatActivity {

    private EditText phoneNumberInput;
    private Button continueButton;
    private Button vkLoginButton;
    private static final int VK_SDK_REQUEST = 100;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        phoneNumberInput = findViewById(R.id.phoneNumberInput);
        continueButton = findViewById(R.id.continueButton);
        vkLoginButton = findViewById(R.id.vkLoginButton);

        VK.initialize(getApplicationContext());

        continueButton.setOnClickListener(v -> {
            String phoneNumber = phoneNumberInput.getText().toString();
            if (phoneNumber.length() == 12) {
                sendVerificationRequest(phoneNumber);
            } else {
                Toast.makeText(MainActivity.this, "Номер должен содержать 12 цифр.", Toast.LENGTH_SHORT).show();
            }
        });

        vkLoginButton.setOnClickListener(v -> {
            List<VKScope> scopes = Arrays.asList(VKScope.FRIENDS, VKScope.WALL, VKScope.PHOTOS);
            VK.login(this, scopes);
        });
    }


    private void sendVerificationRequest(String phoneNumber) {
        Retrofit retrofit = new Retrofit.Builder()
                .baseUrl("YOUR_API_BASE_URL")
                .addConverterFactory(GsonConverterFactory.create())
                .build();
        VerificationApi apiService = retrofit.create(VerificationApi.class);

        Call<Void> call = apiService.sendVerificationCode(phoneNumber);
        call.enqueue(new Callback<Void>() {
            @Override
            public void onResponse(Call<Void> call, Response<Void> response) {
                if (response.isSuccessful()) {
                    Intent intent = new Intent(MainActivity.this, VerificationActivity.class);
                    intent.putExtra("phoneNumber", phoneNumber);
                    startActivity(intent);
                } else {
                    Toast.makeText(MainActivity.this, "Ошибка отправки запроса: " + response.code(), Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(Call<Void> call, Throwable t) {
                Toast.makeText(MainActivity.this, "Ошибка сети: " + t.getMessage(), Toast.LENGTH_SHORT).show();
            }
        });
    }


    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (requestCode == VK_SDK_REQUEST) {
            VK.onActivityResult(requestCode, resultCode, data, new VKAuthCallback() {
                @Override
                public void onLogin(VKAccessToken token) {
                    Intent intent = new Intent(MainActivity.this, MainAfterLogin.class);
                    startActivity(intent);
                }
                @Override
                public void onLoginFailed(VKAccessToken token) {
                    Toast.makeText(MainActivity.this, "Вход через VK не удался", Toast.LENGTH_SHORT).show();
                }
            });
        }
        super.onActivityResult(requestCode, resultCode, data);
    }
}
