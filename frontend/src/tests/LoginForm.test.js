import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import Login from '../page/loginPage';

// Мок для fetch API
global.fetch = jest.fn();

// Вспомогательная функция для рендера компонента с роутером
const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

// Перед каждым тестом сбрасываем моки
beforeEach(() => {
  fetch.mockClear();
  localStorage.clear();
  // Мок для window.location.reload
  Object.defineProperty(window, 'location', {
    writable: true,
    value: { reload: jest.fn() }
  });
});

describe('Login Form Component', () => {
  test('рендерится форма авторизации по умолчанию', () => {
    renderWithRouter(<Login />);
    
    expect(screen.getByText('Вход в личный кабинет')).toBeInTheDocument();
    expect(screen.getByLabelText('Логин')).toBeInTheDocument();
    expect(screen.getByLabelText('Пароль')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Войти' })).toBeInTheDocument();
  });
  
  test('переключается на форму регистрации при клике', () => {
    renderWithRouter(<Login />);
    
    fireEvent.click(screen.getByText('Регистрация'));
    
    expect(screen.getByText('Новый пользователь')).toBeInTheDocument();
    expect(screen.getByLabelText('Фамилия')).toBeInTheDocument();
    expect(screen.getByLabelText('Имя')).toBeInTheDocument();
    expect(screen.getByLabelText('Отчество')).toBeInTheDocument();
  });
  
  test('показывает ошибку при неправильном формате email в форме логина', async () => {
    renderWithRouter(<Login />);
    
    // Настраиваем мок fetch для возврата ошибки
    fetch.mockImplementationOnce(() => 
      Promise.resolve({
        ok: false,
        json: () => Promise.resolve({
          detail: "Invalid email format. Please enter a valid email address."
        })
      })
    );
    
    // Заполняем форму логина некорректными данными
    fireEvent.change(screen.getByLabelText('Логин'), { target: { value: 'неправильныйимейл' } });
    fireEvent.change(screen.getByLabelText('Пароль'), { target: { value: 'password123' } });
    
    // Отправляем форму
    fireEvent.submit(screen.getByRole('button', { name: 'Войти' }));
    
    // Ждем, пока появится сообщение об ошибке
    await waitFor(() => {
      expect(screen.getByText("Invalid email format. Please enter a valid email address.")).toBeInTheDocument();
    });
  });
  
  test('показывает ошибку при вводе неверного пароля', async () => {
    renderWithRouter(<Login />);
    
    // Настраиваем мок fetch для возврата ошибки аутентификации
    fetch.mockImplementationOnce(() => 
      Promise.resolve({
        ok: false,
        json: () => Promise.resolve({
          detail: "Incorrect password."
        })
      })
    );
    
    // Заполняем форму логина
    fireEvent.change(screen.getByLabelText('Логин'), { target: { value: 'correct@example.com' } });
    fireEvent.change(screen.getByLabelText('Пароль'), { target: { value: 'wrongpassword' } });
    
    // Отправляем форму
    fireEvent.submit(screen.getByRole('button', { name: 'Войти' }));
    
    // Ждем, пока появится сообщение об ошибке
    await waitFor(() => {
      expect(screen.getByText("Incorrect password.")).toBeInTheDocument();
    });
  });
  
  test('успешная авторизация перенаправляет пользователя', async () => {
    renderWithRouter(<Login />);
    
    // Настраиваем мок fetch для успешного ответа
    fetch.mockImplementationOnce(() => 
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({
          access_token: 'fake_access_token',
          refresh_token: 'fake_refresh_token',
          token_type: 'bearer'
        })
      })
    );
    
    // Заполняем форму логина
    fireEvent.change(screen.getByLabelText('Логин'), { target: { value: 'valid@example.com' } });
    fireEvent.change(screen.getByLabelText('Пароль'), { target: { value: 'correctpassword' } });
    
    // Отправляем форму
    fireEvent.submit(screen.getByRole('button', { name: 'Войти' }));
    
    // Проверяем, что токены были сохранены в localStorage
    await waitFor(() => {
      expect(localStorage.getItem('access_token')).toBe('fake_access_token');
      expect(localStorage.getItem('refresh_token')).toBe('fake_refresh_token');
      // Проверяем, что произошло перенаправление
      expect(window.location.reload).toHaveBeenCalled();
    });
  });
});

describe('Register Form Component', () => {
  test('показывает ошибку при попытке зарегистрировать пользователя с существующим email', async () => {
    renderWithRouter(<Login />);
    
    // Переключаемся на вкладку регистрации
    fireEvent.click(screen.getByText('Регистрация'));
    
    // Настраиваем мок fetch для возврата ошибки
    fetch.mockImplementationOnce(() => 
      Promise.resolve({
        ok: false,
        json: () => Promise.resolve({
          detail: "The user with this email already exists in the system."
        })
      })
    );
    
    // Заполняем форму регистрации
    fireEvent.change(screen.getByLabelText('Фамилия'), { target: { value: 'Существующий' } });
    fireEvent.change(screen.getByLabelText('Имя'), { target: { value: 'Пользователь' } });
    fireEvent.change(screen.getByLabelText('Отчество'), { target: { value: 'Отчество' } });
    fireEvent.change(screen.getByLabelText('Логин'), { target: { value: 'existing@example.com' } });
    fireEvent.change(screen.getByLabelText('Пароль'), { target: { value: 'password123' } });
    
    // Отправляем форму
    const registerButton = screen.getByRole('button', { name: 'Войти' });
    fireEvent.submit(registerButton);
    
    // Ждем, пока появится сообщение об ошибке
    await waitFor(() => {
      expect(screen.getByText("The user with this email already exists in the system.")).toBeInTheDocument();
    });
  });
  
  test('показывает ошибку при попытке регистрации с коротким паролем', async () => {
    renderWithRouter(<Login />);
    
    // Переключаемся на вкладку регистрации
    fireEvent.click(screen.getByText('Регистрация'));
    
    // Настраиваем мок fetch для возврата ошибки
    fetch.mockImplementationOnce(() => 
      Promise.resolve({
        ok: false,
        json: () => Promise.resolve({
          detail: "Password must be at least 6 characters long."
        })
      })
    );
    
    // Заполняем форму регистрации
    fireEvent.change(screen.getByLabelText('Фамилия'), { target: { value: 'Тест' } });
    fireEvent.change(screen.getByLabelText('Имя'), { target: { value: 'Короткий' } });
    fireEvent.change(screen.getByLabelText('Отчество'), { target: { value: 'Пароль' } });
    fireEvent.change(screen.getByLabelText('Логин'), { target: { value: 'test@example.com' } });
    fireEvent.change(screen.getByLabelText('Пароль'), { target: { value: 'abc' } });  // Короткий пароль
    
    // Отправляем форму
    const registerButton = screen.getByRole('button', { name: 'Войти' });
    fireEvent.submit(registerButton);
    
    // Ждем, пока появится сообщение об ошибке
    await waitFor(() => {
      expect(screen.getByText("Password must be at least 6 characters long.")).toBeInTheDocument();
    });
  });
  
  test('успешная регистрация перенаправляет пользователя', async () => {
    renderWithRouter(<Login />);
    
    // Переключаемся на вкладку регистрации
    fireEvent.click(screen.getByText('Регистрация'));
    
    // Настраиваем мок fetch для успешного ответа
    fetch.mockImplementationOnce(() => 
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({
          access_token: 'new_user_access_token',
          refresh_token: 'new_user_refresh_token',
          token_type: 'bearer'
        })
      })
    );
    
    // Заполняем форму регистрации
    fireEvent.change(screen.getByLabelText('Фамилия'), { target: { value: 'Новый' } });
    fireEvent.change(screen.getByLabelText('Имя'), { target: { value: 'Пользователь' } });
    fireEvent.change(screen.getByLabelText('Отчество'), { target: { value: 'Тестович' } });
    fireEvent.change(screen.getByLabelText('Логин'), { target: { value: 'new@example.com' } });
    fireEvent.change(screen.getByLabelText('Пароль'), { target: { value: 'password123' } });
    
    // Отправляем форму
    const registerButton = screen.getByRole('button', { name: 'Войти' });
    fireEvent.submit(registerButton);
    
    // Проверяем, что токены были сохранены в localStorage
    await waitFor(() => {
      expect(localStorage.getItem('access_token')).toBe('new_user_access_token');
      expect(localStorage.getItem('refresh_token')).toBe('new_user_refresh_token');
      // Проверяем, что произошло перенаправление
      expect(window.location.reload).toHaveBeenCalled();
    });
  });
  
  test('показывает ошибку при отсутствии соединения с сервером', async () => {
    renderWithRouter(<Login />);
    
    // Настраиваем мок fetch для имитации ошибки сети
    fetch.mockImplementationOnce(() => 
      Promise.reject(new Error('Network Error'))
    );
    
    // Заполняем форму логина
    fireEvent.change(screen.getByLabelText('Логин'), { target: { value: 'test@example.com' } });
    fireEvent.change(screen.getByLabelText('Пароль'), { target: { value: 'password123' } });
    
    // Отправляем форму
    fireEvent.submit(screen.getByRole('button', { name: 'Войти' }));
    
    // Ждем, пока появится сообщение об ошибке
    await waitFor(() => {
      expect(screen.getByText("Произошла ошибка при соединении с сервером")).toBeInTheDocument();
    });
  });
}); 