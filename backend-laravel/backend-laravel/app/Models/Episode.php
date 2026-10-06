<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Episode extends Model
{
    use HasFactory;

    // Разрешаем массовое заполнение этих полей
    protected $fillable = [
        'user_id',
        'filename',
        'file_path',
        'diagnosis_code',
        'quality_score',
        'extracted_facts',
        'check_results',
        'status',
    ];

    // Указываем, что JSON-поля нужно автоматически декодировать в массивы
    protected function casts(): array
    {
        return [
            'extracted_facts' => 'array',
            'check_results' => 'array',
            'quality_score' => 'decimal:2',
        ];
    }

    // Связь с пользователем (врачом), который загрузил эпикриз
    public function user()
    {
        return $this->belongsTo(User::class);
    }
}